#!/usr/bin/env python
"""

"""
import logging
from django.core.management.base import BaseCommand

from solar.models.solar_res import SolarRes
from solar.models.solar_util import SolarUtility
from regions.models import State

_LOGGER = logging.getLogger('django')


class Command(BaseCommand):
    help = 'Scale solar capacity'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true', dest='clear', help=''
        )

    def handle(self, *args, **options):

        lst = [
            'AZ',
            'FL',
            'IL',
            'IA',
            'KY',
            'NE',
            'OH',
            'OK',
            'MO',
            'MA',
            'NJ',
            'CA',
            'NV',
            'WA',
            'CO',
            'HI',
            'NC',
            'PA',
            'TX',
            'NM',
            'DE',
            'OR',
            'VT',
            'NY',
            'MD',
            'UT',
            'GA',
            'MN',
            'IN',
            'RI',
            'TN',
            'CT',
            'SC',
            'KS',
            'VA',
            'ID',
            'WI',
            'MI',
            'AR',
            'AL',
            'MS',
            'ME',
            'SD',
            'MT',
            'WY',
            'LA',
            'DC',
            'NH',
            'ND',
            'WV',
            'AK',
        ]
        
        eiasum = [0.0] * len(lst)

        count = 0
        for state in lst:
            solarutilis = SolarUtility.objects.filter(state=state)
            for ut in solarutilis:
                try:
                    eiasum[count] = eiasum[count] + float(ut.dc_mw)
                except:
                    pass

            count = count + 1
        
        lst2 = [
            'Arizona',
            'Florida',
            'Illinois',
            'Iowa',
            'Kentucky',
            'Nebraska',
            'Ohio',
            'Oklahoma',
            'Missouri',
            'Massachusetts',
            'New Jersey',
            'California',
            'Nevada',
            'Washington',
            'Colorado',
            'Hawaii',
            'North Carolina',
            'Pennsylvania',
            'Texas',
            'New Mexico',
            'Delaware',
            'Oregon',
            'Vermont',
            'New York',
            'Maryland',
            'Utah',
            'Georgia',
            'Minnesota',
            'Indiana',
            'Rhode Island',
            'Tennessee',
            'Connecticut',
            'South Carolina',
            'Kansas',
            'Virginia',
            'Idaho',
            'Wisconsin',
            'Michigan',
            'Arkansas',
            'Alabama',
            'Mississippi',
            'Maine',
            'South Dakota',
            'Montana',
            'Wyoming',
            'Louisiana',
            'Washington DC',
            'New Hampshire',
            'North Dakota',
            'West Virginia',
            'Alaska',
        ]
        
        ressum = [0.0] * len(lst2)
       
        count = 0
        for state in lst2:
            try:
                solarresi = SolarRes.objects.filter(state=state)
                for re in solarresi:
                    ressum[count] = ressum[count] + float(re.dc_kw)
                count = count + 1
            except:
                pass

        
        ratios = [0.0] * len(lst2)

        count = 0
        for state in lst2:
            
            try:
                seiastate = State.objects.get(name=state)
                ratios[count] = (float(seiastate.seia_dc_mw) - eiasum[count]) / (
                    ressum[count] / 1000
                )
                count = count + 1
            except:
                ratios[count] = 0
                count = count + 1

        # Because hawaii is in MW already
        index = lst2.index("Hawaii")
        ratios[index] = ratios[index] / 1000

        #ratios = ['1.717561861946','1.0','4.350657632441','19.000562831129','1.480805517852','6.997789431226','1.476325695667','1.272802202057','1.656525403001','1.407600439660','1.348783075377','1.633026353289','5.181606167443','2.047917160938','1.808149098787','2.300997683948','9.938112456868','4.500713437725','4.660530748898','1.506625003250','3.411249161969','1.813758652984','1.0','1.750307221631','8.355558492933','10.101432635282','14.128520249287','5.929544651245','5.785306921339','32.775820219714','3.293031829683','2.276756779409','14.104440550531','4.591607911054','1.369895080143','25.558803091953','3.702747953166','2.045073396832','18.244691825360','1.0','4.579452150807','14.171024940330','1.0','7.332500858475','20.322352121470','1.005563481405','1.494191885602','1.606443310591','1.0','6.016492282894','4.169561446107']

        for solarresi in SolarRes.objects.all():
            if solarresi.state != "N/A":
                try:
                    index = lst2.index(solarresi.state)
                    solarresi.scaled_dc_kw = (
                        solarresi.scaled_dc_kw * float(ratios[index])
                    )
                    solarresi.save()
                except:
                    pass

        for s in State.objects.all():
            if s.name in lst2:
                index = lst2.index(s.name)
                s.res_ratio = (
                    float(ratios[index])
                )
                s.save()
