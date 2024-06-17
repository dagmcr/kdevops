#!/usr/bin/env python3
# SPDX-License-Identifier: copyleft-next-0.3.1
import os
import subprocess
import sys
import logging
import argparse
import time
import yaml
import json
import urllib.request
from typing import List, Union, Dict


def popen(
    cmd: list[str], environ: dict[str, str] = {}, comm: bool = True
) -> dict[str, object]:
    try:
        logging.debug(f"{' '.join(cmd)}")
        p = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environ
        )
        if comm:
            stdout, stderr = p.communicate()
            if stdout:
                logging.debug(stdout.decode("utf-8"))
            if stderr:
                logging.debug(stderr.decode("utf-8"))
            logging.debug(f"Return code: {p.returncode}")
        return {"process": p, "stdout": stdout.decode("utf-8")}
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)


def parser():
    parser = argparse.ArgumentParser(description="Git Reference generate tool")
    # parser.add_argument('--foo', action='store_true', help='foo is great option')
    parser.add_argument("--debug", action="store_true", help="debug")
    parser.add_argument(
        "--output",
        help="output file",
        required=True,
    )
    parser.add_argument(
        "--force", action="store_true", help="always generate output file"
    )
    parser.add_argument(
        "--prefix",
        help="the Kconfig CONFIG prefix to use (e.g. BOOTLINUX_TREE_LINUS)",
        required=True,
    )
    parser.add_argument(
        "--extra",
        help="extra configs (yaml)",
    )

    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid subcommands",
        help="additional help",
        dest="cmd",
    )
    gitref = subparsers.add_parser("gitref", help="git-ref tool (git-ls-remote)")
    gitref.add_argument(
        "--repo",
        help="the upstream repository to check tags with git-ls-remote",
        required=True,
    )
    gitref.add_argument(
        "--filter-heads",
        help="user additional ref filter for heads command",
        default="*",
    )
    gitref.add_argument(
        "--filter-tags",
        help="user additional ref filter for tags command",
        default="*",
    )
    gitref.add_argument(
        "--refs",
        type=int,
        default=1,
        help="number of references",
        required=True,
    )
    kreleases = subparsers.add_parser("kreleases", help="kernel.org/releases.json")
    kreleases.add_argument(
        "--moniker",
        help="moniker (mainline, stable, longterm or linux-next)",
        required=True,
    )
    return parser


def check_file_date(file):
    if not os.path.exists(file):
        return True
    modified_time = os.path.getmtime(file)
    current_time = time.time()
    if current_time - modified_time > 86400:
        return True
    return False


def _ref_generator_choices_static(args, conf_name, ref_name, ref_help):
    refs = {}
    with open(args.output, "a") as f:
        logging.debug("static: {}".format(ref_name))
        refs.update({ref_name: conf_name})
        f.write("config {}\n".format(conf_name))
        # Do overwrite ref when custom
        if "_CUSTOM_REF_NAME" in ref_name:
            f.write('\tbool "custom"\n')
        else:
            f.write('\tbool "{}"\n'.format(ref_name))
        if ref_help:
            f.write("\thelp\n")
            f.write("\t\t{}\n\n".format(ref_help))
        else:
            f.write("\n")
    return refs


def _ref_generator_choices(args, reflist, id) -> Dict[str, str]:
    refs = {}
    # for refline in reflist.splitlines():
    for ref_name in reflist:
        logging.debug("{id}: {ref}".format(id=id, ref=ref_name))
        config = "{prefix}_REF_{id}".format(prefix=args.prefix, id=id)
        refs.update({ref_name: config})
        with open(args.output, "a") as f:
            f.write("config {}\n".format(config))
            f.write('\t bool "{}"\n\n'.format(ref_name))
        id += 1
    return refs


def ref_generator(args, reflist, extraconfs) -> None:
    """Generate output file. Example:

    choice
        prompt "Tag or branch to use"

    config BOOTLINUX_TREE_NEXT_REF_0
             bool "akpm"

    config BOOTLINUX_TREE_NEXT_REF_1
             bool "akpm-base"

    config BOOTLINUX_TREE_NEXT_REF_2
             bool "master"

    config BOOTLINUX_TREE_NEXT_REF_3
             bool "pending-fixes"

    config BOOTLINUX_TREE_NEXT_REF_4
             bool "stable"

    endchoice

    config BOOTLINUX_TREE_NEXT_REF
            string
            default "akpm" if BOOTLINUX_TREE_NEXT_REF_0
            default "akpm-base" if BOOTLINUX_TREE_NEXT_REF_1
            default "master" if BOOTLINUX_TREE_NEXT_REF_2
            default "pending-fixes" if BOOTLINUX_TREE_NEXT_REF_3
            default "stable" if BOOTLINUX_TREE_NEXT_REF_4
    """
    if os.path.exists(args.output):
        os.remove(args.output)
    refs: dict[str, str] = {}

    with open(args.output, "a") as f:
        f.write("# SPDX-License-Identifier: copyleft-next-0.3.1\n")
        f.write("# Automatically generated file\n")
        if "gitref" in args.cmd and args.refs != 0:
            f.write("\nif HAVE_{}_GITREF\n\n".format(args.prefix))
        if ("gitref" in args.cmd and args.refs == 0) or "kreleases" in args.cmd:
            f.write("\nif !HAVE_{}_GITREF\n\n".format(args.prefix))
        f.write("choice\n")
        f.write('\tprompt "Tag or branch to use"\n\n')

    logging.debug("Generating...")
    refs.update(_ref_generator_choices(args, reflist, len(refs)))

    if extraconfs:
        for config in extraconfs:
            refs.update(
                _ref_generator_choices_static(
                    args, config["config"], config["ref"], config["help"]
                )
            )

    with open(args.output, "a") as f:
        f.write("endchoice\n\n")
        f.write("config {}_REF\n".format(args.prefix))
        f.write("\tstring\n")
        for r in refs.keys():
            # Do not include quotes when using CUSTOM_REF_NAME
            if "_CUSTOM_REF_NAME" in r:
                f.write("\tdefault {ref} if {conf}\n".format(ref=r, conf=refs[r]))
            else:
                f.write('\tdefault "{ref}" if {conf}\n'.format(ref=r, conf=refs[r]))
        if "gitref" in args.cmd:
            f.write("\nendif # HAVE_{}_GITREF\n".format(args.prefix))
        if ("gitref" in args.cmd and args.refs == 0) or "kreleases" in args.cmd:
            f.write("\nendif # !HAVE_{}_GITREF\n".format(args.prefix))


def remote(args) -> List:
    heads = popen(
        [
            "git",
            "-c",
            "versionsort.suffix=-",
            "ls-remote",
            "--sort=-version:refname",
            "--heads",
            args.repo,
            args.filter_heads,
        ]
    )
    tags = popen(
        [
            "git",
            "-c",
            "versionsort.suffix=-",
            "ls-remote",
            "--sort=-version:refname",
            "--tags",
            args.repo,
            args.filter_tags,
        ]
    )

    return [heads["stdout"], tags["stdout"]]


def gitref_getreflist(args, reflist):
    refs = []
    for refline in reflist.splitlines():
        if "^{}" in refline:
            continue
        if len(refs) >= args.refs:
            break
        ref_name = refline.split("/")[-1]
        refs.append(ref_name)
        logging.debug("release: {}".format(ref_name))
    return refs


def _get_extraconfs(args) -> List[Dict[str, Union[str, None]]]:
    extraconfs = []
    if args.extra:
        if os.path.exists(args.extra):
            with open(args.extra, mode="rt") as f:
                yml = yaml.safe_load(f)
                extraconfs = yml["configs"]
    return extraconfs


def gitref(args) -> None:
    """Get git reference list using git-ls-remote."""

    refstr = remote(args)
    reflist = []
    for rl in refstr:
        _refs = gitref_getreflist(args, rl)
        for r in _refs:
            reflist.append(r)

    ref_generator(args, reflist, _get_extraconfs(args))


def kreleases(args) -> None:
    """Get the latest kernel releases from kernel.org/releases.json"""

    with urllib.request.urlopen("https://www.kernel.org/releases.json") as url:
        data = json.load(url)

    reflist = []
    for release in data["releases"]:
        if release["moniker"] == args.moniker:
            reflist.append(release["version"])

    ref_generator(args, reflist, _get_extraconfs(args))


def main() -> None:
    """Kconfig choice generator for git refereces"""
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    p = parser()
    args, _ = p.parse_known_args()
    if args.debug:
        log.setLevel(logging.DEBUG)

    if not args.force and not check_file_date(args.output):
        logging.debug("File already updated")
        return

    cmd_disp = {"gitref": gitref, "kreleases": kreleases}

    cmd_disp[args.cmd](args)


if __name__ == "__main__":
    ret = 0
    try:
        main()
    except Exception:
        ret = 1
        import traceback

        traceback.print_exc()
    sys.exit(ret)
