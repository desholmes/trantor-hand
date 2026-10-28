# Trantor

[Specimens and usage](https://desholmes.github.io/trantor-type/) · [Download the latest release](https://github.com/desholmes/trantor-type/releases/latest)

Three fonts based on the lettering of the Apple TV+ series *Foundation*, each extended with a lowercase, a SemiBold and the characters for everyday UK English (café, naïve, façade, £, €). They are modified versions of Roger Sperberg's OFL fonts, renamed because the original names are reserved.

| Family              | Based on                                                                          | Use it for                               | Stylistic set 1                        |
| ------------------- | --------------------------------------------------------------------------------- | ---------------------------------------- | -------------------------------------- |
| **Trantor Hand**    | [Foundation Titles Hand](https://github.com/rsperberg/foundation-titles-hand) 0.85 | Titles, headings and short text          | Dotted o and crossed w                 |
| **Trantor Caption** | [Foundation One](https://github.com/rsperberg/foundation-one) 0.4                  | Labels and captions, usually in capitals | Dotted e, like E                       |
| **Trantor Mark**    | [Foundation Logo](https://github.com/rsperberg/foundation-logo) 0.3                | Wordmarks and a few large words          | Capitals from the thinner logo (`salt`) |

Every family has Regular (400) and SemiBold (600) weights.

## Using the fonts

On the web, load the series stylesheet from a release, or self-host [fonts/](fonts/):

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/desholmes/trantor-type@v1.0.0/fonts/trantor.css" />
```

```css
h1, h2 { font-family: "Trantor Mark", sans-serif; font-weight: 600; }
body   { font-family: "Trantor Hand", sans-serif; }
.label { font-family: "Trantor Caption", sans-serif; text-transform: uppercase; letter-spacing: 0.04em; }
.titles { font-feature-settings: "ss01"; }
```

Each family also has its own stylesheet in `fonts/<family>/webfonts/`. Desktop TTFs are in `fonts/<family>/ttf/` and in the release zips. Each family's [specimen page](https://desholmes.github.io/trantor-type/) covers its stylistic set, spacing and install notes.

## Licence

The fonts are licensed under the SIL Open Font License 1.1 ([OFL.txt](OFL.txt); each family's folder in [families/](families/) has its own copy and FONTLOG). You can use, embed and modify them, but not sell them on their own, and the licence must go with them when you redistribute them. The build tooling and the site are MIT-licensed ([LICENSE-CODE](LICENSE-CODE)).

*Foundation* is an Apple TV+ series based on the Isaac Asimov books. These fan-made fonts aren't affiliated with or endorsed by Apple, Skydance or the Asimov estate. The font licence doesn't cover the show's trademarks.

## Contributing

To build the fonts, change a glyph or make a release, see [CONTRIBUTING.md](CONTRIBUTING.md).
