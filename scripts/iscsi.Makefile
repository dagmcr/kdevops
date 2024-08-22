ifeq (y,$(CONFIG_KDEVOPS_ENABLE_ISCSI))

ISCSI_EXTRA_ARGS += iscsi_target_wwn='$(subst ",,$(CONFIG_ISCSI_TARGET_WWN))'
ISCSI_EXTRA_ARGS += iscsi_target_pv_prefix='$(subst ",,$(CONFIG_ISCSI_TARGET_PV_PREFIX))'
ISCSI_EXTRA_ARGS += iscsi_target_pv_count='$(subst ",,$(CONFIG_ISCSI_TARGET_PV_COUNT))'
ISCSI_EXTRA_ARGS += kdevops_enable_iscsi=true

ANSIBLE_EXTRA_ARGS += $(ISCSI_EXTRA_ARGS)

iscsi:
	$(Q)ansible-playbook $(ANSIBLE_VERBOSE) --extra-vars=@$(KDEVOPS_EXTRA_VARS) \
		-f 30 -i hosts -l iscsi playbooks/iscsi.yml

KDEVOPS_BRING_UP_DEPS += iscsi

PHONY += iscsi

endif
