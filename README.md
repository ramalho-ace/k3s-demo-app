# k3s-demo-app (demo)

Demo simples com Redis e PostgreSQL e um backend Flask que expõe um contador de cliques.

Arquivos principais:
- `app/` - código do backend (Flask) e `Dockerfile`.
- `manifests/` - manifests Kubernetes para `postgres`, `redis` e `demo-app`.

Como testar localmente (ex.: k3s ou minikube):

1) Build e push com Google Cloud Build (GCR):

```bash
gcloud builds submit --config=cloudbuild.yaml . --project=YOUR_PROJECT_ID
```

Isso criará e enviará a imagem para `gcr.io/YOUR_PROJECT_ID/k3s-demo-app-backend:latest`.

2) Alternativa: build local e tag para seu registry:

```bash
docker build -t k3s-demo-app/backend:latest ./app
```

3) Aplicar manifests no cluster:

```bash
kubectl apply -f manifests/
```

4) Acesse o serviço `demo-app`:
- Se estiver usando NodePort (o `manifests/service.yaml` expõe `nodePort:30090`), acesse `http://<node-ip>:30090/`.

Observações:
- O banco Postgres usa credenciais de demonstração `demo/demo`; em produção, troque por Secrets e PVCs.
- Redis está incluído como serviço, mas o backend demo escreve/ler apenas no Postgres.

Script de build & push
----------------------

Se preferir usar um script local para build e push para o Artifact Registry, há um utilitário no repositório:

- `build-and-push.sh` — builda a imagem e faz push para `REGION-docker.pkg.dev/PROJECT/REPO/IMAGE:TAG`.

Uso:

```bash
chmod +x build-and-push.sh
./build-and-push.sh [VERSION]
```

Exemplo (usa `latest` por padrão):

```bash
./build-and-push.sh
```

O script já vem pré-configurado com:

- `PROJECT_ID="offshore-hub-foundations"`
- `REGION="southamerica-east1"`
- `REPO_NAME="offshore-hub-repo"`
- `IMAGE_NAME="python-app"`

Altere as variáveis no início do script se necessário.
