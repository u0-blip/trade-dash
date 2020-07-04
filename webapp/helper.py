import os
import pickle
import numpy as np

pi = 3.1415926

class Page():
    def __init__(self, *args, **kwargs):
        self.width_label = 13


    def input_3(self, field, default, var):
        vcmd = self.register(self.validate) # we have to wrap the command
        f = tk.Frame(self)
        l = tk.Label(f, text=field+':', width=self.width_label)
        l.pack(side=tk.LEFT, anchor = tk.N, padx=5, pady=5)
        for i in range(len(default)):
            e = tk.Entry(f, validate="key", validatecommand=(vcmd, '%P'), width=12)
            e.insert(0, default[i])
            e.pack(side=tk.LEFT, anchor = tk.W)
        f.pack(anchor = tk.W)

    def drop_down(self, menu):
        tkvar = tk.StringVar(self)

        # Dictionary with options
        tkvar.set(menu[0]) # set the default option

        f = tk.Frame(self)
        popupMenu = tk.OptionMenu(f, tkvar, *menu)
        tk.Label(f, text="Choose a shape").pack(side=tk.LEFT, anchor = tk.W)
        popupMenu.pack(side=tk.LEFT, anchor = tk.W)
        f.pack(anchor = tk.W)

        # on change dropdown value
        def change_dropdown(*args):
            print( tkvar.get() )

        # link function to change dropdown
        tkvar.trace('w', change_dropdown)

    def fields_input(self, fields):
        info = {
            'check_box': [],
            'radio_btn' : [],
            'input_range': [],
            'input': []
        }

        for field, default in fields.items(): 

            if not isinstance(default, list):
                #input 
                info['input'].append([field, default])

            elif isinstance(default[0], float) or isinstance(default[0], int):
                #input range
                info['input_range'].append([field, *default])

            elif isinstance(default[0], str):
                info['radio_btn'].append([field, *default])
                # drop down list
        return info

    def sweep_fields_input(self, sweep_fields):
        field_name = ['field name', 'start', 'end', 'num param']

        f = tk.Frame(self)
        for f_n in field_name:
            l = tk.Label(f, text=f_n, width=self.width_label)
            l.pack(side=tk.LEFT, anchor = tk.N, padx=5, pady=5)
        f.pack(anchor = tk.W)

        var = []
        for field, default in self.sweep_fields.items(): 
            self.input_3(field, default, var)

    def validate(self, new_text):
        if not new_text: # the field is being cleared
            self.guess = None
            return True

        try:
            guess = float(new_text)
            return True
        except ValueError:
            return False

    def size_distri_btn(self):
        label = tk.Label(self, text='Particle size distribution type', anchor = tk.W)
        label.pack(side="top", fill="x", expand=False)

        distri_types = ['fixed', 'gaussian']

        R1 = tk.Radiobutton(self, text=distri_types[0], variable=self.distri_type, value=distri_types[0], command=self.sel)
        R1.pack( anchor = tk.W )

        R2 = tk.Radiobutton(self, text=distri_types[1], variable=self.distri_type, value=distri_types[1], command=self.sel)
        R2.pack( anchor = tk.W )

    def sel(self):
        print(self.distri_type.get())

    def show(self):
        self.lift()

class geo(Page):

    fields = {
        'particle_size' : [0.05, 0.12, 5],
        'x_loc' : [0, -3.4, 1],
        'distance' : [1, 3, 1],
        'fill_factor' : [0.5, 0.7, 5],
        'std' : [0.1, 0.3, 1],
        'rotation' : 7*pi/6,
        'pml_thick' : 0.5,
        'num_particles' : 2,
        'shape_types' : ['sphere', 'triangle', 'hexagon', 'cube'],
        'solid_center' : [-2, 0, 0],
        'cell_size':  [10, 10, 10],
    }

    
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.info = self.fields_input(self.fields)

class sim(Page):
    fields ={
        'sim_types'  :  ['checker', 'simple shape', 'voronoi'],
        'type'  :  'checker',
        'dimension'  :  2,
        'resolution'  :  60,
        'change_res'  :  1,
        'time'  :  1000,
        'out_every'  :  0.2,
        'save_every'  :  30
    }

    calc_flux = 0
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.info = self.fields_input(self.fields)

class general(Page):
    fields  =  {
        'verbals'  :  1,
        'gen vor'  :  0,
        'meep sim'  :  1,
        'gen gmsh'  :  0,
        'process inp'  :  0,
        'clean array'  :  0,
        'sim abq'  :  1,
    }

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.info = self.fields_input(self.fields)

class source(Page):
    fields  =  {
        'mode_types'  :  ['normal', 'gaussian', 'far_field_transform', 'waveguide'],
        'mode'  :  'normal',
        'fcen'  :  0.8167,
        'tilt_angle'  :  0,
        'sigma'  :  2,
        'amp'  :  100,
        'flux_nfreq'  :  100,
        'fwidth'  :  2,
        'flux_width'  :  0.8,
        'size'  :  [0, 10, 0],
        'center'  :  [4, 0, 0],
        'near_flux_loc'  :  [3.5, 0, 0],
        'far_flux_loc'  :  [-4.5, 0, 0],
        'flux_size'  :  [0, 9, 0],
    }

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.info = self.fields_input(self.fields)

class visualization(Page):
    fields  =  {
        '3d_plotting_axis'  :  'x',
        'structure'  :  0,
        'transiant'  :  0,
        'rms'  :  0,
        'view_only_particles'  :  1,
        'frame_speed'  :  300,
        'log_res'  :  0,

        'cbar_scale'  :  [0, 0.0002],
        'viz_offset'  :  [0, 0, 0]
    }

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.info = self.fields_input(self.fields)
