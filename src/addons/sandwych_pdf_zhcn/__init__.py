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

from openerp.tools.config import config
from reportlab.lib.styles import ParagraphStyle
try:
    import openerp.report.render.rml2pdf.customfonts as cfonts
except ImportError:
    import report.render.rml2pdf.customfonts as cfonts

# 方便的常量
__MODULE_NAME = 'sandwych_pdf_zhcn'
__SANS_FONT = 'WenQuanYi Zen Hei'
__MONO_FONT = 'WenQuanYi Zen Hei Mono'
__SERIF_FONT = 'AR PL SungtiL GB'

def find_font_path():
    paths = config['addons_path'].split(',')
    for ap in paths:
        my_path = path.join(ap, __MODULE_NAME, 'fonts')
        if path.isdir(my_path):
            return my_path

    raise IOError('Cannot found path "sandwych_pdf_zhcn" in "addons_path"')

#设置中文换行
ParagraphStyle.defaults['wordWrap'] = 'CJK'

my_font_path = find_font_path()

# 注入我们自己的字体路径
for k, v in cfonts.TTFSearchPathMap.iteritems():
    v.append(my_font_path)

# 修改字体映射
cfonts.CustomTTFonts = [ 
    ('Helvetica', __SANS_FONT, 'hei.ttc', 'normal'),
    ('Helvetica', __SANS_FONT, 'hei.ttc', 'bold'),
    ('Helvetica', __SANS_FONT, 'hei.ttc', 'italic'),
    ('Helvetica', __SANS_FONT, 'hei.ttc', 'bolditalic'),
    ('Times', __SERIF_FONT, 'song.ttf', 'normal'),
    ('Times', __SERIF_FONT, 'song.ttf', 'bold'),
    ('Times', __SERIF_FONT, 'song.ttf', 'italic'),
    ('Times', __SERIF_FONT, 'song.ttf', 'bolditalic'),
    ('Times-Roman', __SERIF_FONT, 'song.ttf', 'normal'),
    ('Times-Roman', __SERIF_FONT, 'song.ttf', 'bold'),
    ('Times-Roman', __SERIF_FONT, 'song.ttf', 'italic'),
    ('Times-Roman', __SERIF_FONT, 'song.ttf', 'bolditalic'),
    ('Courier', __MONO_FONT, 'hei.ttc', 'normal'),
    ('Courier', __MONO_FONT, 'hei.ttc', 'bold'),
    ('Courier', __MONO_FONT, 'hei.ttc', 'italic'),
    ('Courier', __MONO_FONT, 'hei.ttc', 'bolditalic'),
    ('Monospace', __MONO_FONT, 'hei.ttc', 'bolditalic'),

    # 为公司默认设置的页眉/页脚处理字体
    ('DejaVu Sans', __SANS_FONT, 'hei.ttc', 'normal'),
    ('DejaVu Sans Bold', __SANS_FONT, 'hei.ttc', 'bold'),
    ('DejaVuSans', __SANS_FONT, 'hei.ttc', 'normal'),
    ('DejaVuSansBold', __SANS_FONT, 'hei.ttc', 'bold'),

    # Alias for custom reports
    ('SimHei', __SANS_FONT, 'hei.ttc', 'normal'),
    ('SimHei', __SANS_FONT, 'hei.ttc', 'bold'),
    ('SimHei', __SANS_FONT, 'hei.ttc', 'italic'),
    ('SimHei', __SANS_FONT, 'hei.ttc', 'bolditalic'),
    ('SimSun', __SERIF_FONT, 'song.ttf', 'normal'),
    ('SimSun', __SERIF_FONT, 'song.ttf', 'bold'),
    ('SimSun', __SERIF_FONT, 'song.ttf', 'italic'),
    ('SimSun', __SERIF_FONT, 'song.ttf', 'bolditalic'),
]

