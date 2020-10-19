# Norniring the BGP Fabric

Automating the deployment of a BGP fabric with Nornir **version 3** (You can go back to nornir version 2 by using `git checkout 80bfa9dcb5b4c25d83cabc8a44d1b822e5c779bb`)

This basically reproduce exactly the fabric done here but using Nornir: [FullyAutomatedBGPfabric](https://github.com/jpmondet/FullyAutomatedBGPfabric)

Hence, this deployment is aimed at debian-based Linux targets only (including Cumulus Linux).

## Prerequisites

On a recent system, you should be good to go simply with `pip install -r requirements.txt`

However, Nornir needs at least python 3.6 and there are still a whole lot of devices using older versions.

If you have an older python version (**or if you are using CITC**), you should use this to install python 3.6.3 and all the dependencies to use Nornir :

```bash
curl -LO https://raw.githubusercontent.com/jpmondet/norniring-bgpfabric/master/resources/add-compatible-python.sh ; chmod u+x add-compatible-python.sh ; source add-compatible-python.sh
```

This use `pyenv` on one specific directory and a `virtualenv` so it should not mess up with the rest of your system.

**NOTE**: The ssh keys are already distributed on CITC so this is not handled by the script.

## Deploying the Fabric

If you are on CITC, this is pretty straightforward : `python deploy_network.py`

Elsewhere, you'll have to update the inventory.

This repo uses an Ansible's style inventory so you have to update the `hosts` file and the `host_vars` and/or `group_vars` directories.
