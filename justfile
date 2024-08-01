default:
    just --list

pre-commit:
    pre-commit run --all-files

init *conf="test":
    cp --recursive conf {{ conf }}
    find {{ conf }}/ -name "*.sample" -exec sh -c 'mv "$0" "${0%.sample}"' {} \;
    ./scripts/genvars.sh {{ conf }}/vars/extra.yml
