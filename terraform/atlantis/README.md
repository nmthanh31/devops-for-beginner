# Atlantis on the local Kubernetes cluster

## Current status

- Namespace `atlantis` has been created in the local cluster.
- Helm chart repository `runatlantis` is configured in the local `.helm/` cache.
- The Atlantis release is **not installed yet** because the GitLab hostname,
  project path, HTTPS callback URL, PAT and webhook secret are environment-specific.

## Install after filling local values

```powershell
Copy-Item values.example.yaml values.local.yaml
# Edit values.local.yaml; never commit it.

$helmCfg = Join-Path (Get-Location) '.helm'
$env:HELM_CONFIG_HOME = $helmCfg
$kc = (Resolve-Path 'terraform/k8s-config/local-rancher.yaml').Path

helm upgrade --install atlantis runatlantis/atlantis `
  --namespace atlantis `
  --create-namespace `
  --kubeconfig $kc `
  --values terraform/atlantis/values.local.yaml
```

After the release creates the `atlantis` ServiceAccount, apply the Lab3-only
permissions needed by the Kubernetes provider:

```powershell
kubectl --kubeconfig $kc apply -f terraform/atlantis/lab3-rbac.yaml
```

For a first smoke test, keep both ingresses disabled and use port-forward:

```powershell
kubectl --kubeconfig $kc -n atlantis port-forward svc/atlantis 4141:80
```

The browser UI is then available at `http://localhost:4141`. GitLab cannot send
webhooks to localhost; enabling real PR automation requires an HTTPS ingress
reachable from the company GitLab and a webhook URL ending in `/events`.

## Lab3 state backend

Lab3 uses the Kubernetes backend with the state Secret in namespace `atlantis`.
The Atlantis service account must be granted access to that Secret and to the
target namespace (`tf-lab3-stag`) before an Atlantis `apply` is attempted.
