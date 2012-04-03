# encoding: utf-8
# @author: Wei Li <liwei@sandwych.com>
# @date: 2012-04-03

##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from os import path

from reportlab.lib.styles import ParagraphStyle
from openerp.tools.config import config

__MODULE_NAME = 'sandwych_pdf_zhcn'

try:
    import openerp.report.render.rml2pdf.customfonts as cfonts
except ImportError:
    import report.render.rml2pdf.customfonts as cfonts

def find_font_path():
    paths = config['addons_path'].split(',')
    for ap in paths:
        my_path = path.join(ap, __MODULE_NAME, 'fonts')
        if path.isdir(my_path):
            return my_path

    raise IOError("Cannot found path 'sandwych_pdf_zhcn' in 'addons_path'")


my_font_path = find_font_path()

# 注入我们自己的字体路径
for k, v in cfonts.TTFSearchPathMap.iteritems():
    v.append(my_font_path)

# 修改字体映射
cfonts.CustomTTFonts = [ 
    ('Helvetica',"WenQuanYi Zen Hei", "hei.ttc", 'normal'),
    ('Helvetica',"WenQuanYi Zen Hei", "hei.ttc", 'bold'),
    ('Helvetica',"WenQuanYi Zen Hei", "hei.ttc", 'italic'),
    ('Helvetica',"WenQuanYi Zen Hei", "hei.ttc", 'bolditalic'),
    ('Times',"AR PL SungtiL GB", "song.ttf", 'normal'),
    ('Times',"AR PL SungtiL GB", "song.ttf", 'bold'),
    ('Times',"AR PL SungtiL GB", "song.ttf", 'italic'),
    ('Times',"AR PL SungtiL GB", "song.ttf", 'bolditalic'),
    ('Times-Roman',"AR PL SungtiL GB", "song.ttf", 'normal'),
    ('Times-Roman',"AR PL SungtiL GB", "song.ttf", 'bold'),
    ('Times-Roman',"AR PL SungtiL GB", "song.ttf", 'italic'),
    ('Times-Roman',"AR PL SungtiL GB", "song.ttf", 'bolditalic'),
    ('Courier',"WenQuanYi Zen Hei", "hei.ttc", 'normal'),
    ('Courier',"WenQuanYi Zen Hei", "hei.ttc", 'bold'),
    ('Courier',"WenQuanYi Zen Hei", "hei.ttc", 'italic'),
    ('Courier',"WenQuanYi Zen Hei", "hei.ttc", 'bolditalic'),

    # 为公司默认设置的页眉/页脚处理字体
    ('DejaVu Sans',"WenQuanYi Zen Hei", "hei.ttc", 'normal'),
    ('DejaVu Sans Bold',"WenQuanYi Zen Hei", "hei.ttc", 'bold'),
    ('DejaVuSans',"WenQuanYi Zen Hei", "hei.ttc", 'normal'),
    ('DejaVuSansBold',"WenQuanYi Zen Hei", "hei.ttc", 'bold'),

    # Alias for custom reports
    ('SimHei',"WenQuanYi Zen Hei", "hei.ttc", 'normal'),
    ('SimHei',"WenQuanYi Zen Hei", "hei.ttc", 'bold'),
    ('SimHei',"WenQuanYi Zen Hei", "hei.ttc", 'italic'),
    ('SimHei',"WenQuanYi Zen Hei", "hei.ttc", 'bolditalic'),
    ('SimSun',"song", "song.ttf", 'normal'),
    ('SimSun',"song", "song.ttf", 'bold'),
    ('SimSun',"song", "song.ttf", 'italic'),
    ('SimSun',"song", "song.ttf", 'bolditalic'),
]

