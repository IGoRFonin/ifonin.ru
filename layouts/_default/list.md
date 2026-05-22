{{- /* Markdown-представление списка (главная, разделы) для AI-агентов. */ -}}
---
title: {{ .Title | jsonify }}
description: {{ or .Params.description .Site.Params.description | jsonify }}
url: {{ .Permalink | jsonify }}
---

# {{ .Title }}
{{ with .RawContent }}
{{ . | strings.TrimSpace }}
{{ end }}
{{- range .RegularPagesRecursive.ByDate.Reverse }}
- [{{ .Title }}]({{ .Permalink }}){{ if not .Date.IsZero }} — {{ .Date.Format "2006-01-02" }}{{ end }}
{{- end }}
