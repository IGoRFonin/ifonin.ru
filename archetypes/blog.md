---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
lastmod: {{ .Date }}
description: ""
tags: []
slug: "{{ .File.ContentBaseName }}"
draft: true
---
