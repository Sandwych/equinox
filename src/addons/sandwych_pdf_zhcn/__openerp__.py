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
{
    "name" : "中文报表支持",
    "version" : "0.1",
    "author" : "Sandwych Consulting Limited.",
    "maintainer":"Wei Li <liwei@sandwych.com>",
    "website": "http://www.sandwych.com",
    "description": """
        PDF 中文报表支持

        安装此模块以后 PDF 报表的页眉页脚也还可能仍为乱码。
        若出现此情况请进入系统“公司”设置中将“页眉页脚里的“DejaVu Sans 英文”等字体设置换成“WenQuanYi Zen Hei”后保存即可。
    """,
    "depends" : ["base"],
    "category" : "Generic Modules/Base",
    "demo_xml" : [],
    "update_xml" : [],
    "license": "GPL-3",
    "installable": True,
    "auto_install": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
