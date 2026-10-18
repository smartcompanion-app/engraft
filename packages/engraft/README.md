<p align="center">
  <img alt="engraft" src="https://raw.githubusercontent.com/smartcompanion-app/engraft/main/assets/engraft-logo.svg" height="72">
</p>

**Apply customizations to any project without templating placeholders.**

Your repository stays clean and runnable. The customization lives beside it, in
two files: a **template** the maintainer writes, declaring what can be
customized and where it lives, and a **values** file the consumer writes, with
their choices.

```shell
npm install -g @smartcompanion/engraft
```

```yaml
# engraft.template.yml — shipped with the project
variables:
  app_name:
    description: Application name
    default: DefaultApp

customizations:
  - action: json_replace
    file: config.json
    replace:
      - selector: $.name
        variable: app_name
```

```yaml
# engraft.values.yml — kept outside the project, one per brand or customer
app_name: MyApp
```

```shell
engraft apply --template engraft.template.yml --values engraft.values.yml
```

Four actions cover JSON (`json_replace`), HTML via XPath (`html_replace`), any
text file via regex (`regex_replace`) and whole-file swaps (`file_replace`).
Every action runs against a staging copy first, so a failure leaves the project
exactly as it was.

## Documentation

**[smartcompanion-app.github.io/engraft](https://smartcompanion-app.github.io/engraft/)**
— getting started, the template and values reference, every action, and the
CLI.

## License

[BSD 2-Clause](https://github.com/smartcompanion-app/engraft/blob/main/LICENSE).
