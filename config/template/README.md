# Validation Dashboard — file layout

template/
├── report.html          # Main Jinja template (ALL {{ ... }} variables live here)
├── css/
│   ├── dashboard.css    # reset, layout, overview, metrics, pkg rows, popup
│   ├── sidebar.css      # sidebar + fixed profile icon
│   ├── sections.css     # accordion + detail panel (nav bar, collapse) + logs
│   ├── graphs.css       # graphs section + chart tables
│   ├── profile.css      # profile page
│   └── snake.css        # snake HUD + canvas
├── js/
│   ├── utils.js         # renderChartTable, exportChartPng
│   ├── navigation.js    # showSection, toggleSidebar
│   ├── graphs.js        # all Chart.js charts + setGraphView
│   ├── sections.js      # accordion, showDetails, prev/next, collapse
│   ├── profile.js       # loadProfileData, showStats, confetti
│   ├── snake.js         # snake game
│   └── app.js           # entry: avatar, default nav, file:// blocker
└── assets/
    ├── icons/           # logo referenced as assets/icons/{{ icon_path }}
    └── images/

## How the server data reaches the JS
report.html renders ONE inline bootstrap block:

    var REPORT = { total, passed, failed, sectionLabels, sectionPass, sectionFail };
    window.REPORT = REPORT;

Every external .js file reads from `REPORT` and contains NO Jinja, so the
.js/.css files are fully static and cacheable.

## Script load order (already set in report.html)
utils → navigation → graphs → sections → profile → snake → app

## Serving notes
Links in report.html are RELATIVE (css/..., js/..., assets/...).
If you serve css/js from Flask's /static folder instead, change the tags to:
    <link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
and move the css/ js/ assets/ folders under static/.
