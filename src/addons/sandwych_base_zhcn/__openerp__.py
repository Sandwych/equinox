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
    "name" : "基本系统中文支持",
    "version" : "0.1",
    "author" : "Sandwych Consulting Limited.",
    "maintainer":"Wei Li <liwei@sandwych.com>",
    "website": "http://www.sandwych.com",
    "description": """
        基本系统中文支持

        此模块将在创建数据库时自动安装
        1. 将默认的本位币从欧元设置为人民币，并调整汇率
        2. 重新设置公司的页眉页脚解决乱码问题
    """,
    "depends" : ['base', 'sandwych_pdf_zhcn'],
    "category" : "Generic Modules/Base",
    "demo_xml" : [],
    "update_xml" : ['base_data.xml'],
    "license": "GPL-3",
    "installable": True,
    "auto_install": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
