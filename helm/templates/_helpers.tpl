{{/*
展開 chart 的名稱
*/}}
{{- define "kubewizard.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
創建完整的名稱（用於資源命名）
*/}}
{{- define "kubewizard.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
創建 chart 名稱和版本
*/}}
{{- define "kubewizard.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
通用標籤
*/}}
{{- define "kubewizard.labels" -}}
helm.sh/chart: {{ include "kubewizard.chart" . }}
{{ include "kubewizard.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
選擇器標籤
*/}}
{{- define "kubewizard.selectorLabels" -}}
app.kubernetes.io/name: {{ include "kubewizard.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
創建 ServiceAccount 名稱
*/}}
{{- define "kubewizard.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "kubewizard.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Redis 服務名稱
*/}}
{{- define "kubewizard.redis.fullname" -}}
{{- printf "%s-redis" (include "kubewizard.fullname" .) }}
{{- end }}

{{/*
Redis URL
*/}}
{{- define "kubewizard.redis.url" -}}
{{- if .Values.redis.enabled }}
{{- printf "redis://%s:6379/0" (include "kubewizard.redis.fullname" .) }}
{{- else if .Values.redis.externalUrl }}
{{- .Values.redis.externalUrl }}
{{- else }}
{{- "redis://localhost:6379/0" }}
{{- end }}
{{- end }}

{{/*
Secret 名稱
*/}}
{{- define "kubewizard.secretName" -}}
{{- if .Values.existingSecret }}
{{- .Values.existingSecret }}
{{- else }}
{{- include "kubewizard.fullname" . }}
{{- end }}
{{- end }}
