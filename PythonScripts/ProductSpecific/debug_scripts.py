import sys


def force_wake_gt():
    print("Force waking GT")
    import __main__
    sv = __main__.sv
    sv.gfxcard0.tile0.uncore.pcie.usp.cfg.linksts.show()
    sv.gfxcard0.tile0.uncore.sgunit.pcicmd_pci.bme=1
    sv.gfxcard0.tile0.uncore.sgunit.pcicmd_pci.mae=1
    sv.gfxcard0.tile0.uncore.sgunit.pcicmd_pci.show
    sv.gfxcard0.tile0.uncore.sgunit.devicectl_pci.urre = 0
    sv.gfxcard0.tile0.uncore.sgunit.devicectl_pci.fee = 0
    sv.gfxcard0.tile0.uncore.sgunit.devicectl_pci.nfee = 0
    sv.gfxcard0.tile0.uncore.sgunit.devicectl_pci.cee = 0
    sv.gfxcard0.tile0.uncore.sgunit.devicectl_pci.show
    sv.socket0.uncore.pcie.pxp2.port0.cfg.errcormsk = 0xffffffff
    sv.socket0.uncore.pcie.pxp2.port0.cfg.erruncmsk = 0xffffffff
    sv.socket0.uncore.pcie.pxp2.port0.cfg.rootctl.sefee = 0
    sv.socket0.uncore.pcie.pxp2.port0.cfg.rootctl.senfee = 0
    sv.socket0.uncore.pcie.pxp2.port0.cfg.rootctl.secee = 0 
    sv.gfxcard0.tile0.gfx.gtgp.gdrst.init_gfxfull_sr=0x1
    sv.gfxcard0.tile0.gfx.gtgp.gdrst.init_gfxfull_sr  #result should be 0x0
        
    if not (sv.gfxcard0.tile0.gfx.gtgp.force_wake == 0x10001):
        print ("GT is asleep, now going to wake it up.")
        sv.gfxcard0.tile0.gfx.gtgp.force_wake = 0x10001
        print ("GT current status is %s" %sv.gfxcard0.tile0.gfx.gtgp.force_wake)
    else:
        print ("GT current status is %s" %sv.gfxcard0.tile0.gfx.gtgp.force_wake)


def get_pcie_status():
    if r'C:\PythonSV\icelakex\pcie' not in sys.path: sys.path.append(r'C:\PythonSV\icelakex\pcie')
    import icelakex.pcie.ltssm_icx as ltssm 
    ltssm.showActiveLanes() 
    import fv.PCIe.EIPPCIeStatus as eip
    status = eip.iouLinkStatus()
    print(status)
    return status
