{{- /* Markdown-представление страницы для AI-агентов (Accept: text/markdown). */ -}}
---
title: {{ .Title | jsonify }}
description: {{ or .Params.description .Site.Params.description | jsonify }}
url: {{ .Permalink | jsonify }}
{{- if not .Date.IsZero }}
date: {{ .Date.Format "2006-01-02" }}
{{- end }}
{{- with .Params.tags }}
tags: {{ . | jsonify }}
{{- end }}
---

# {{ .Title }}

{{ .RawContent | strings.TrimSpace }}
