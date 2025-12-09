# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 10:31:00 2019

@author: Work
"""

import os
import subprocess
from jinja2 import Environment, FileSystemLoader


def render_template(output_name, kwargs):
    
    src = "{}_template.pdf_tex".format(output_name)
    dst = "{}.pdf_tex".format(output_name)
    
    env = Environment(block_start_string = '\BLOCK{',
                      block_end_string = '}',
                      variable_start_string = '\VAR{',
                      variable_end_string = '}',
                      comment_start_string = '\#{',
                      comment_end_string = '}',
                      line_statement_prefix = None,
                      line_comment_prefix = '%',
                      trim_blocks = True,
                      autoescape = False,
                      loader=FileSystemLoader('.'))
    template = env.get_template(src)
    rendered = template.render(**kwargs)
    
    with open(dst, 'w') as f:
        f.write(rendered)
    
    return


def compile_image(output_name):
    
    tex = "{}.tex".format(output_name)
    aux = "{}.aux".format(output_name)
    log = "{}.log".format(output_name)
    
    subprocess.call(['pdflatex', '-shell-escape', tex])
    os.remove(aux)
    os.remove(log)
    
    return


if __name__ == "__main__":
    
    images = ['floating_device',
              'floating_device_top',
              'fixed_device']
    
    float_kwargs = {"height": "$H = 15m$",
                    "width": "$W = 10m$",
                    "draft": "$T = 10m$",
                    "hubheight": "$H_{R} = -8m$",
                    "mass": "{\small $G = [0, 0, -5]$}",
                    "umb": "{\small $U = [0, 0, -10]$}",
                    "foundation": {"one": "$F_{A1} = [50, 86.6, 0]$",
                                 "two": "$F_{A2} = [50, -86.6, 0]$",
                                 "three": "$F_{A3} = [-100, 0, 0]$"},
                    "fairlead": {"one": "$F_{L1} = [2.5, 4.33, -10]$",
                               "two": "$F_{L2} = [2.5, -4.33, -10]$",
                               "three": "$F_{L3} = [-5, 0, -10]$"},
                    "foundrad": "$F_{R} = 100m$"
                    }
    
    fixed_kwargs = {"height": "$H = 35m$",
                    "width": "$W = 10m$",
                    "length": "$L = 14m$",
                    "hubheight": "$H_{R} = 30m$",
                    "mass": "$G = [0, 0, 15]$",
                    "foundation": {"one": "$F_{A1} = [7, 0, 0]$"}
                    }
    
    kwargs_list = [float_kwargs, float_kwargs, fixed_kwargs]
    
    for image, kwargs in zip(images, kwargs_list):
        render_template(image, kwargs)
        compile_image(image)
    
