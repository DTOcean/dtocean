# -*- coding: utf-8 -*-
"""
Created on Mon May 30 16:40:43 2016

@author: francesco
"""

import os

import numpy as np

from . import file_utilities as f_u


class DataStructure:
    def __init__(self, data_dic, force_read_flag=False):
        self.data_dic = data_dic
        self.general_inputs = data_dic["inputs_hydrodynamic"]["general_input"]
        self.input_type = self.general_inputs["input_type"]
        self.project_folder = data_dic["prj_folder"]
        self.precompiled_case = None
        self.get_array_mat = self.general_inputs["get_array_mat"]

        if self.input_type == 2:
            self.data_folder = os.path.join(self.project_folder, "hydrodynamic")
        else:
            self.data_folder = data_dic["inputs_hydrodynamic"]["general_input"][
                "data_folder"
            ]

        if self.input_type == 4:
            self.general_inputs = data_dic["inputs_hydrodynamic"][
                "general_input"
            ]
        elif self.input_type == 3:
            nbody = 0
            freq_def = []
            ang_def = []
            if os.path.isfile(os.path.join(self.data_folder, "nemoh.cal")):
                with open(
                    os.path.join(self.data_folder, "nemoh.cal"), "r"
                ) as fid:
                    lines = fid.readlines()
                nbody = f_u.split_string(lines[6], int, sep=None)[0]
                water_depth = f_u.split_string(lines[3], sep=None)[0]
                line_ind = 7
                for bb in range(nbody):
                    ndof = f_u.split_string(
                        lines[line_ind + 3],
                        int,
                        sep=None,
                    )[0]
                    line_ind += 3 + ndof * 2 + 3
                freq_def = f_u.split_string(lines[line_ind + 1], sep=None)
                ang_def = f_u.split_string(lines[line_ind + 2], sep=None)
                line_ind += 2 + 6
                cyl_fea = [0, 0, 0]
                if len(lines) >= line_ind:
                    cyl_fea = f_u.split_string(lines[line_ind], sep=None)

            data_dic["inputs_hydrodynamic"]["general_input"][
                "frequency_def"
            ] = np.array(freq_def)
            data_dic["inputs_hydrodynamic"]["general_input"]["angle_def"] = (
                np.array(ang_def)
            )
            data_dic["inputs_hydrodynamic"]["general_input"]["water_depth"] = (
                np.array(water_depth)
            )
            data_dic["inputs_hydrodynamic"]["general_input"]["cyl_nzeta"] = int(
                cyl_fea[1]
            )
            data_dic["inputs_hydrodynamic"]["general_input"]["cyl_ntheta"] = (
                int(cyl_fea[2])
            )

            self.data_dic = data_dic
            self.general_inputs = data_dic["inputs_hydrodynamic"][
                "general_input"
            ]
            self.body_inputs = data_dic["inputs_hydrodynamic"]["body_inputs"]
            for bi_k in self.body_inputs["body"].keys():
                ch_p = self.body_inputs["body"][bi_k]["child_dof_position"]
                if isinstance(ch_p, int):
                    ch_p = self.body_inputs["body"][bi_k]["number_child"] = 0
                else:
                    ch_p = self.body_inputs["body"][bi_k]["number_child"] = len(
                        ch_p
                    )

            for bi_k in self.body_inputs["body"].keys():
                dof_p = self.body_inputs["body"][bi_k]["dof_with_parent"]
                if isinstance(dof_p, int):
                    dof_p = self.body_inputs["body"][bi_k]["extended_dof"] = 0
                else:
                    dof_p = self.body_inputs["body"][bi_k]["extended_dof"] = (
                        len(dof_p)
                    )

            for bi_k in self.body_inputs["body"].keys():
                rel_path = self.body_inputs["body"][bi_k]["mesh"]
                self.body_inputs["body"][bi_k]["mesh"] = os.path.join(
                    self.project_folder, "raw_data", rel_path
                )

        else:
            self.body_inputs = data_dic["inputs_hydrodynamic"]["body_inputs"]

            ang_v = np.linspace(
                0,
                360.0,
                int(self.general_inputs["angle_def"][0]),
                endpoint=False,
            )
            self.general_inputs["angle_def"] = [
                int(self.general_inputs["angle_def"][0]),
                ang_v.min(),
                ang_v.max(),
            ]

            for bi_k in self.body_inputs["body"].keys():
                ch_p = self.body_inputs["body"][bi_k]["child_dof_position"]
                if isinstance(ch_p, int):
                    ch_p = self.body_inputs["body"][bi_k]["number_child"] = 0
                else:
                    ch_p = self.body_inputs["body"][bi_k]["number_child"] = len(
                        ch_p
                    )

            for bi_k in self.body_inputs["body"].keys():
                dof_p = self.body_inputs["body"][bi_k]["dof_with_parent"]
                if isinstance(dof_p, int):
                    dof_p = self.body_inputs["body"][bi_k]["extended_dof"] = 0
                else:
                    dof_p = self.body_inputs["body"][bi_k]["extended_dof"] = (
                        len(dof_p)
                    )

            for bi_k in self.body_inputs["body"].keys():
                rel_path = self.body_inputs["body"][bi_k]["mesh"]
                self.body_inputs["body"][bi_k]["mesh"] = os.path.join(
                    self.project_folder, "raw_data", rel_path
                )

            if force_read_flag:
                self.input_type = 3

    def check_inputs(self):
        # call the specific check for the different case
        errStr = []
        if self.input_type == 1:
            pass
        elif self.input_type == 2:
            if (
                self.general_inputs["get_array_mat"]
                and self.general_inputs["water_depth"] == 0
            ):
                errStr.append(
                    "the array interaction cannot be assessed with infinite water depth"
                )
                return (False, errStr)

        elif self.input_type == 3:
            pass
        elif self.input_type == 4:
            pass
        else:
            return (False,)

        return (True,)
