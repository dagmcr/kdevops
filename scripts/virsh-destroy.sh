#!/bin/bash
# SPDX-License-Identifier: copyleft-next-0.3.1

for i in $(virsh list | awk '{print $2'}| grep kdevops); do
	echo $i
	virsh destroy $i
done
