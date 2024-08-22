ifeq (y,$(CONFIG_KDEVOPS_SETUP_SMBD))

SMBD_EXTRA_ARGS += smbd_share_device_prefix='$(subst ",,$(CONFIG_SMBD_SHARE_DEVICE_PREFIX))'
SMBD_EXTRA_ARGS += smbd_share_device_count='$(subst ",,$(CONFIG_SMBD_SHARE_DEVICE_COUNT))'
SMBD_EXTRA_ARGS += smbd_share_fstype='$(subst ",,$(CONFIG_SMBD_SHARE_FSTYPE))'
SMBD_EXTRA_ARGS += smbd_share_path='$(subst ",,$(CONFIG_SMBD_SHARE_PATH))'
SMBD_EXTRA_ARGS += smb_root_pw='$(subst ",,$(CONFIG_SMB_ROOT_PW))'
SMBD_EXTRA_ARGS += kdevops_smbd_enable=True

ANSIBLE_EXTRA_ARGS += $(SMBD_EXTRA_ARGS)

smbd:
	$(Q)ansible-playbook $(ANSIBLE_VERBOSE) --extra-vars=@$(KDEVOPS_EXTRA_VARS) \
		-f 30 -i hosts -l smbd playbooks/smbd.yml

KDEVOPS_BRING_UP_DEPS += smbd

PHONY += smbd

endif
