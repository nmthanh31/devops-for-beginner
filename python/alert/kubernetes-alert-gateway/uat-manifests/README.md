# Apply Kubernetes Alert Gateway to UAT

These are plain Kubernetes YAML manifests. Apply the YAML files directly; Kustomize is not used.

- Context: `local`
- Namespace: `cattle-monitoring-system`
- Existing app Secret: `alert-webhook-secret`
- Existing Valkey Cluster: service `valkey-cluster-bootstrap` in namespace `valkey-cluster`
- Gateway image: `uat-harbor-lab.vnpost.vn/cloud-dept-alert/kubernetes-webhook-alert:uat-20261023-01`

Create the Harbor pull Secret from Git Bash:

```bash
read -r -p 'UAT Harbor username: ' UAT_HARBOR_USER
read -r -s -p 'UAT Harbor password: ' UAT_HARBOR_PASSWORD; echo
kubectl --context local create secret docker-registry uat-harbor-pull \
  -n cattle-monitoring-system \
  --docker-server=uat-harbor-lab.vnpost.vn \
  --docker-username="$UAT_HARBOR_USER" \
  --docker-password="$UAT_HARBOR_PASSWORD" \
  --dry-run=client -o yaml | kubectl --context local apply -f -
unset UAT_HARBOR_USER UAT_HARBOR_PASSWORD
```

The Valkey cluster requires authentication. Copy its password into an app-namespace Secret; this
command does not print the password:

```bash
VALKEY_PASSWORD="$(kubectl --context local get secret valkey-cluster-auth \
  -n valkey-cluster -o jsonpath='{.data.password}' | base64 -d)"
kubectl --context local create secret generic alert-webhook-valkey-auth \
  -n cattle-monitoring-system \
  --from-literal=REDIS_PASSWORD="$VALKEY_PASSWORD" \
  --dry-run=client -o yaml | kubectl --context local apply -f -
unset VALKEY_PASSWORD
```

Apply manifests and wait for the rollout:

```bash
kubectl --context local apply -f .deploy/kubernetes/uat-manifests/*.yaml
kubectl --context local rollout status deployment/alert-webhook -n cattle-monitoring-system
kubectl --context local get pods -n cattle-monitoring-system -l app.kubernetes.io/name=kubernetes-webhook-alert
kubectl --context local logs deployment/alert-webhook -n cattle-monitoring-system --tail=100
```

If the Harbor project or image tag differs, update the image in `04-alert-webhook-deployment.yaml`.
