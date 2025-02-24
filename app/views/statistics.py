from collections import defaultdict, Counter
from datetime import datetime
from typing import Any
from django.db.models import Value
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.timezone import get_current_timezone
from django.utils.translation import gettext as _
import re

from app.models import Analytics
from .common import get_build_version

def _count_dict(dict: defaultdict[Any, set], counter: Counter):
    return [(len(v), counter[k], k) for k, v in dict.items()]

def statistics(request: HttpRequest) -> HttpResponse:
    if not request.user.has_perm('app.view_analytics'):
        return HttpResponseForbidden()

    year = request.GET.get('year', '')
    tz = get_current_timezone()

    if not re.match(r'^\d{4}$', year):
        now = datetime.now(tz=tz)
        year = str(now.year)
        return redirect(reverse('statistics') + '?year=' + year)

    year = int(year)
    this_year = datetime(year, 1, 1, tzinfo=tz)
    next_year = datetime(year + 1, 1, 1, tzinfo=tz)
    qs = Analytics.objects.filter(isbot=Value(0), created_at__gte=this_year, created_at__lt=next_year).exclude(country=Value(''))

    by_month_visitors = defaultdict(set)
    by_month_views = Counter()
    by_country_visitors = defaultdict(set)
    by_country_views = Counter()

    for item in qs.iterator():
        created_at = item.created_at.astimezone(tz)
        month = created_at.strftime("%B")
        by_month_views[month] += 1
        by_month_visitors[month].add(item.ip)
        country = _country_names.get(item.country, _country_names['XX'])
        by_country_views[country] += 1
        by_country_visitors[country].add(item.ip)

    return render(request, 'site/pages/statistics.html', {
        'build_version': get_build_version(),
        'year': year,
        'prev_year': year - 1,
        'next_year': year + 1,
        'by_month': _count_dict(by_month_visitors, by_month_views),
        'by_country': sorted(_count_dict(by_country_visitors, by_country_views), reverse=True),
    })

_country_names = {
    'XX': '(Unknown)',
    'AF': "Afghanistan",
    'AX': "Aland Islands",
    'AL': "Albania",
    'DZ': "Algeria",
    'AS': "American Samoa",
    'AD': "Andorra",
    'AO': "Angola",
    'AI': "Anguilla",
    'AQ': "Antarctica",
    'AG': "Antigua and Barbuda",
    'AR': "Argentina",
    'AM': "Armenia",
    'AW': "Aruba",
    'AU': "Australia",
    'AT': "Austria",
    'AZ': "Azerbaijan",
    'BS': "Bahamas",
    'BH': "Bahrain",
    'BD': "Bangladesh",
    'BB': "Barbados",
    'BY': "Belarus",
    'BE': "Belgium",
    'BZ': "Belize",
    'BJ': "Benin",
    'BM': "Bermuda",
    'BT': "Bhutan",
    'BO': "Bolivia",
    'BQ': "Bonaire, Sint Eustatius and Saba",
    'BA': "Bosnia and Herzegovina",
    'BW': "Botswana",
    'BV': "Bouvet Island",
    'BR': "Brazil",
    'IO': "British Indian Ocean Territory",
    'BN': "Brunei Darussalam",
    'BG': "Bulgaria",
    'BF': "Burkina Faso",
    'BI': "Burundi",
    'CV': "Cabo Verde",
    'KH': "Cambodia",
    'CM': "Cameroon",
    'CA': "Canada",
    'KY': "Cayman Islands",
    'CF': "Central African Republic",
    'TD': "Chad",
    'CL': "Chile",
    'CN': "China",
    'CX': "Christmas Island",
    'CC': "Cocos (Keeling) Islands",
    'CO': "Colombia",
    'KM': "Comoros",
    'CD': "Congo (Kinshasa)",
    'CG': "Congo (Brazzaville)",
    'CK': "Cook Islands",
    'CR': "Costa Rica",
    'HR': "Croatia",
    'CU': "Cuba",
    'CW': "Curaçao",
    'CY': "Cyprus",
    'CZ': "Czechia",
    'CI': "Côte d'Ivoire",
    'DK': "Denmark",
    'DJ': "Djibouti",
    'DM': "Dominica",
    'DO': "Dominican Republic",
    'EC': "Ecuador",
    'EG': "Egypt",
    'SV': "El Salvador",
    'GQ': "Equatorial Guinea",
    'ER': "Eritrea",
    'EE': "Estonia",
    'SZ': "Eswatini",
    'ET': "Ethiopia",
    'FK': "Falkland Islands [Malvinas]",
    'FO': "Faroe Islands",
    'FJ': "Fiji",
    'FI': "Finland",
    'FR': "France",
    'GF': "French Guiana",
    'PF': "French Polynesia",
    'TF': "French Southern Territories",
    'GA': "Gabon",
    'GM': "Gambia",
    'GE': "Georgia",
    'DE': "Germany",
    'GH': "Ghana",
    'GI': "Gibraltar",
    'GR': "Greece",
    'GL': "Greenland",
    'GD': "Grenada",
    'GP': "Guadeloupe",
    'GU': "Guam",
    'GT': "Guatemala",
    'GG': "Guernsey",
    'GN': "Guinea",
    'GW': "Guinea-Bissau",
    'GY': "Guyana",
    'HT': "Haiti",
    'HM': "Heard Island and McDonald Islands",
    'VA': "Holy See",
    'HN': "Honduras",
    'HK': "Hong Kong",
    'HU': "Hungary",
    'IS': "Iceland",
    'IN': "India",
    'ID': "Indonesia",
    'IR': "Iran",
    'IQ': "Iraq",
    'IE': "Ireland",
    'IM': "Isle of Man",
    'IL': "Israel",
    'IT': "Italy",
    'JM': "Jamaica",
    'JP': "Japan",
    'JE': "Jersey",
    'JO': "Jordan",
    'KZ': "Kazakhstan",
    'KE': "Kenya",
    'KI': "Kiribati",
    'KP': "North Korea",
    'KR': "South Korea",
    'KW': "Kuwait",
    'KG': "Kyrgyzstan",
    'LA': "Lao People's Democratic Republic",
    'LV': "Latvia",
    'LB': "Lebanon",
    'LS': "Lesotho",
    'LR': "Liberia",
    'LY': "Libya",
    'LI': "Liechtenstein",
    'LT': "Lithuania",
    'LU': "Luxembourg",
    'MO': "Macao",
    'MG': "Madagascar",
    'MW': "Malawi",
    'MY': "Malaysia",
    'MV': "Maldives",
    'ML': "Mali",
    'MT': "Malta",
    'MH': "Marshall Islands",
    'MQ': "Martinique",
    'MR': "Mauritania",
    'MU': "Mauritius",
    'YT': "Mayotte",
    'MX': "Mexico",
    'FM': "Micronesia",
    'MD': "Moldova",
    'MC': "Monaco",
    'MN': "Mongolia",
    'ME': "Montenegro",
    'MS': "Montserrat",
    'MA': "Morocco",
    'MZ': "Mozambique",
    'MM': "Myanmar",
    'NA': "Namibia",
    'NR': "Nauru",
    'NP': "Nepal",
    'NL': "Netherlands",
    'NC': "New Caledonia",
    'NZ': "New Zealand",
    'NI': "Nicaragua",
    'NE': "Niger",
    'NG': "Nigeria",
    'NU': "Niue",
    'NF': "Norfolk Island",
    'MP': "Northern Mariana Islands",
    'NO': "Norway",
    'OM': "Oman",
    'PK': "Pakistan",
    'PW': "Palau",
    'PS': "Palestine, State of",
    'PA': "Panama",
    'PG': "Papua New Guinea",
    'PY': "Paraguay",
    'PE': "Peru",
    'PH': "Philippines",
    'PN': "Pitcairn",
    'PL': "Poland",
    'PT': "Portugal",
    'PR': "Puerto Rico",
    'QA': "Qatar",
    'MK': "Republic of North Macedonia",
    'RO': "Romania",
    'RU': "Russia",
    'RW': "Rwanda",
    'RE': "Réunion",
    'BL': "Saint Barthélemy",
    'SH': "Saint Helena, Ascension and Tristan da Cunha",
    'KN': "Saint Kitts and Nevis",
    'LC': "Saint Lucia",
    'MF': "Saint Martin (French part)",
    'PM': "Saint Pierre and Miquelon",
    'VC': "Saint Vincent and the Grenadines",
    'WS': "Samoa",
    'SM': "San Marino",
    'ST': "Sao Tome and Principe",
    'SA': "Saudi Arabia",
    'SN': "Senegal",
    'RS': "Serbia",
    'SC': "Seychelles",
    'SL': "Sierra Leone",
    'SG': "Singapore",
    'SX': "Sint Maarten (Dutch part)",
    'SK': "Slovakia",
    'SI': "Slovenia",
    'SB': "Solomon Islands",
    'SO': "Somalia",
    'ZA': "South Africa",
    'GS': "South Georgia and the South Sandwich Islands",
    'SS': "South Sudan",
    'ES': "Spain",
    'LK': "Sri Lanka",
    'SD': "Sudan",
    'SR': "Suriname",
    'SJ': "Svalbard and Jan Mayen",
    'SE': "Sweden",
    'CH': "Switzerland",
    'SY': "Syrian Arab Republic",
    'TW': "Taiwan",
    'TJ': "Tajikistan",
    'TZ': "Tanzania",
    'TH': "Thailand",
    'TL': "Timor-Leste",
    'TG': "Togo",
    'TK': "Tokelau",
    'TO': "Tonga",
    'TT': "Trinidad and Tobago",
    'TN': "Tunisia",
    'TR': "Turkey",
    'TM': "Turkmenistan",
    'TC': "Turks and Caicos Islands",
    'TV': "Tuvalu",
    'UG': "Uganda",
    'UA': "Ukraine",
    'AE': "United Arab Emirates",
    'GB': "United Kingdom",
    'UM': "United States Minor Outlying Islands",
    'US': "United States of America",
    'UY': "Uruguay",
    'UZ': "Uzbekistan",
    'VU': "Vanuatu",
    'VE': "Venezuela",
    'VN': "Viet Nam",
    'VG': "Virgin Islands (British)",
    'VI': "Virgin Islands (U.S.)",
    'WF': "Wallis and Futuna",
    'EH': "Western Sahara",
    'YE': "Yemen",
    'ZM': "Zambia",
    'ZW': "Zimbabwe",
}
