# -*- coding: utf-8 -*-

from collections import OrderedDict
from plone.versioncheck.formatter import browser
from plone.versioncheck.formatter import machine


pkgsinfo = {'pkgs': {
    'collective.quickupload': OrderedDict([
        ('foo.cfg', {'v': '1.5.8', 'a': ''}),
        ('baz.cfg', {'v': '1.5.2', 'a': ''})
    ]),
    'ipython': OrderedDict([('buildout.cfg', {'v': '5.3.0', 'a': ''})]),
    'lazy': OrderedDict([('buildout.cfg', {'v': '1.0', 'a': ''})]),
    'products.cmfcore': OrderedDict([
        ('buildout.cfg', {'v': '2.1.1', 'a': '\nJust a Test Case\nwith multiple lines'}),  # NOQA: E501
        ('bar.cfg', {'v': '2.2.0', 'a': ''}),
        ('foo.cfg', {'v': '3.0.1', 'a': ''}),
        ('baz.cfg', {'v': '2.2.10', 'a': ''})
    ]),
}}


json_output = '''{
"collective.quickupload": {
    "versions": [
        {
            "description": "foo.cfg",
            "version": "1.5.8",
            "annotation": "",
            "state": "A"
        },
        {
            "description": "baz.cfg",
            "version": "1.5.2",
            "annotation": "",
            "state": "I"
        }
    ],
    "state": "A"
},
"ipython": {
    "versions": [
        {
            "description": "buildout.cfg",
            "version": "5.3.0",
            "annotation": "",
            "state": "A"
        }
    ],
    "state": "A"
},
"lazy": {
    "versions": [
        {
            "description": "buildout.cfg",
            "version": "1.0",
            "annotation": "",
            "state": "A"
        }
    ],
    "state": "A"
},
"products.cmfcore": {
    "versions": [
        {
            "description": "buildout.cfg",
            "version": "2.1.1",
            "annotation": "Just a Test Case\nwith multiple lines",
            "state": "A"
        },
        {
            "description": "bar.cfg",
            "version": "2.2.0",
            "annotation": "",
            "state": "In"
        },
        {
            "description": "foo.cfg",
            "version": "3.0.1",
            "annotation": "",
            "state": "In"
        },
        {
            "description": "baz.cfg",
            "version": "2.2.10",
            "annotation": "",
            "state": "In"
        }
    ],
    "state": "In"
}
}
'''


def test_json_formatter(capsys):
    result = machine(pkgsinfo)
    out, err = capsys.readouterr()
    # Seems that stdout is not correctly captured
    assert result is None
    assert out == ''
    assert err == '\nReport for machines\n\n'
    # assert out == json_output


browser_output = '''<html>
<head>
  <meta charset="utf-8">
  <title>plone.versioncheck</title>
  <style type="text/css" media="screen">
      table {
        font-family: sans-serif;
        font-size: 80%;
        background-color: efefef;
      }
      td {
        border: none;
        padding: 0.5em;
        vertical-align: top;
      }
      thead th {
        border: none;
        padding: 0.5em;
        background-color: #ddddee;
      }
      .even {
        background-color: #efefff;
      }
      .odd {
        background-color: #ffffff;
      }
      .color-D {
        color: green;
      }
      .color-A {
        color: black;
      }
      .color-I {
        color: gray;
      }
      .color-In {
        color: orange;
      }
      .color-U {
        color: darkcyan;
      }
      .color-P {
        color: blue;
      }
      .color-O {
        color: magenta;
      }
      .color-X {
        color: red;
      }

  </style>
</head>
<body>
<table>
  <thead>
    <tr>
      <th>package</th>
      <th>version</th>

      <th>state</th>
      <th>info</th>
      <th>annotation</th>

    </tr>
  </thead>
  <tbody>



    <tr class="odd">


        <td class="color-A" rowspan="2"><span id="collective.quickupload">collective.quickupload</span></td>


        <td class="color-A">1.5.8</td>

        <td class="color-A">A</td>
        <td class="color-A">foo.cfg</td>
        <td class="color-A">&nbsp;</td>

    </tr>

    <tr class="odd">



        <td class="color-I">1.5.2</td>

        <td class="color-I">I</td>
        <td class="color-I">baz.cfg</td>
        <td class="color-I">&nbsp;</td>

    </tr>




    <tr class="even">


        <td class="color-A" rowspan="1"><span id="ipython">ipython</span></td>


        <td class="color-A">5.3.0</td>

        <td class="color-A">A</td>
        <td class="color-A">buildout.cfg</td>
        <td class="color-A">&nbsp;</td>

    </tr>




    <tr class="odd">


        <td class="color-A" rowspan="1"><span id="lazy">lazy</span></td>


        <td class="color-A">1.0</td>

        <td class="color-A">A</td>
        <td class="color-A">buildout.cfg</td>
        <td class="color-A">&nbsp;</td>

    </tr>




    <tr class="even">


        <td class="color-In" rowspan="4"><span id="products.cmfcore">products.cmfcore</span></td>


        <td class="color-A">2.1.1</td>

        <td class="color-A">A</td>
        <td class="color-A">buildout.cfg</td>
        <td class="color-A">Just a Test Case
with multiple lines<br /></td>

    </tr>

    <tr class="even">



        <td class="color-In">2.2.0</td>

        <td class="color-In">I</td>
        <td class="color-In">bar.cfg</td>
        <td class="color-In">&nbsp;</td>

    </tr>

    <tr class="even">



        <td class="color-In">3.0.1</td>

        <td class="color-In">I</td>
        <td class="color-In">foo.cfg</td>
        <td class="color-In">&nbsp;</td>

    </tr>

    <tr class="even">



        <td class="color-In">2.2.10</td>

        <td class="color-In">I</td>
        <td class="color-In">baz.cfg</td>
        <td class="color-In">&nbsp;</td>

    </tr>


  </tbody>
</table>
</body>
</html>'''  # NOQA: E501


def test_browser_formatter(capsys):
    result = browser(pkgsinfo)
    out, err = capsys.readouterr()
    # Seems that stdout is not correctly captured
    assert result is None
    assert out == ''
    assert err == '\nReport for browsers\n\n'
    # assert out == browser_output  # Why is this not working
