from fractal import create_fractal, calculate_new_coords
import pyqtgraph as pg
from scipy.ndimage import rotate
from PyQt4 import QtGui, QtCore

import sys
import numpy as np
import matplotlib.pyplot as plt

class FracThread(QtCore.QThread):
    update = QtCore.pyqtSignal()
    image = QtCore.pyqtSignal(object)
    def __init__(self, parent, min_x,max_x,min_y,max_y,width,height,iters,
                 real_c,imag_c,upsample,fancy,cmap):
        super(FracThread, self).__init__(parent)
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y 
        self.max_y = max_y
        self.width = width
        self.height = height
        self.iters = iters
        self.real_c = real_c 
        self.imag_c = imag_c
        self.upsample = upsample
        self.fancy = fancy
        self.cmap = cmap
        
    def run(self):
         image_data = create_fractal(self.min_x,self.max_x,self.min_y,
                                     self.max_y,self.width,self.height,
                                     self.iters,self.real_c,self.imag_c,
                                     self.upsample,self.fancy,self.cmap)
         self.image.emit(image_data)
         
         
class ErrorDialog(QtGui.QDialog):
    def __init__(self,error_message):
        super(ErrorDialog,self).__init__()
        self.setWindowTitle("Error!")
        self.error_label = QtGui.QLabel(error_message)
        self.dialog_layout = QtGui.QVBoxLayout()
        self.dialog_layout.addWidget(self.error_label)
        
        self.setLayout(self.dialog_layout)


class RadioButtonWidget(QtGui.QWidget):
    def __init__(self,instruction,button_list,label=None,default_index=0):
        super(RadioButtonWidget,self).__init__()

        if label:
            self.title_label = QtGui.QLabel(label)
        self.radio_button_group_box = QtGui.QGroupBox(instruction)
        self.radio_button_group = QtGui.QButtonGroup()
        
        self.radio_button_list = []
        for button in button_list:
            self.radio_button_list.append(QtGui.QRadioButton(button))
        
        self.set_default(default_index)
        
        
        self.radio_button_layout = QtGui.QVBoxLayout()
        for i,button in enumerate(self.radio_button_list):
            self.radio_button_layout.addWidget(button)
            self.radio_button_group.addButton(button)
            self.radio_button_group.setId(button,i)
        
        self.radio_button_group_box.setLayout(self.radio_button_layout)
        
        self.widget_layout = QtGui.QVBoxLayout()
        if label:
            self.widget_layout.addWidget(self.title_label)
        self.widget_layout.addWidget(self.radio_button_group_box)
        
        self.setLayout(self.widget_layout)
        
    
    def set_default(self,default_index):
        for i,button in enumerate(self.radio_button_list):
            if i == default_index:
                button.setChecked(True)
            else:
                button.setChecked(False)
    
    def selected_button(self):
        return self.radio_button_group.checkedId()


class ColorMapSelector(QtGui.QWidget):
    def __init__(self,default_cmap='gnuplot2'):
        super(ColorMapSelector,self).__init__()
        
        cmaps = get_colormaps()
        self.cmap_dict = {}
        for i,cmap in enumerate(cmaps):
            self.cmap_dict[cmap] = i
        self.combo_label = QtGui.QLabel('Color Map:')
        self.combo_box = QtGui.QComboBox()
        self.combo_box.addItems(cmaps)
        self.combo_box.setCurrentIndex(self.cmap_dict[str(default_cmap)])
        self.combo_layout = QtGui.QHBoxLayout()
        self.combo_layout.addWidget(self.combo_label)
        self.combo_layout.addWidget(self.combo_box)
        
        self.setLayout(self.combo_layout)
        
    def selected_colormap(self):
        return self.combo_box.currentText()
    
    def set_default(self,default_cmap):
        self.combo_box.setCurrentIndex(self.cmap_dict[default_cmap])

class FractalParameters(QtGui.QWidget):
    def __init__(self,frac_type,settings=None):
        super(FractalParameters,self).__init__()
        self.inited_check = False
        if settings is None:
            self.inited_check = True
            settings = {'x_min': '-2.0',
                        'x_max' : '1.0',
                        'y_min' : '-1.0',
                        'y_max' : '1.0',
                        'c_real': '-0.7269',
                        'c_imag': '0.1889',
                        'fancy_or_fast': 0,
                        'cmap' : 'gnuplot2',
                        'upsample' : '2'
                        }
        
        self.frac = frac_type
        
        self.x_min_label = QtGui.QLabel('Real Value Min:')
        self.x_max_label = QtGui.QLabel('Real Value Max:')
        self.y_min_label = QtGui.QLabel('Imaginary Value Min:')
        self.y_max_label = QtGui.QLabel('Imaginary Value Max:')
        
        self.x_min_edit = QtGui.QLineEdit()
        self.x_max_edit = QtGui.QLineEdit()
        self.y_min_edit = QtGui.QLineEdit()
        self.y_max_edit = QtGui.QLineEdit()
        
        self.x_min_edit.setText(settings['x_min'])
        self.x_max_edit.setText(settings['x_max'])
        self.y_min_edit.setText(settings['y_min'])
        self.y_max_edit.setText(settings['y_max'])
        if frac_type == 'Julia':
            
            self.c_real_label = QtGui.QLabel('C Real Part:')
            self.c_imag_label = QtGui.QLabel('C Imaginary Part:')
            
            self.c_real_edit = QtGui.QLineEdit()
            self.c_imag_edit = QtGui.QLineEdit()
            
            self.c_real_edit.setText(settings['c_real'])
            self.c_imag_edit.setText(settings['c_imag'])
            if self.inited_check:
                self.x_min_edit.setText('-1.0')
            
        
        self.graphics_buttons = RadioButtonWidget('Graphics Type', 
                                                  ['Fancy','Fast'], 
                                                  default_index = settings['fancy_or_fast'])
        
        self.upsample_label = QtGui.QLabel('Upsampling Rate:')
        self.upsample_edit = QtGui.QLineEdit()
        self.upsample_edit.setText(settings['upsample'])
        
        self.upsample_layout = QtGui.QGridLayout()
        self.upsample_widget = QtGui.QWidget()
        self.upsample_layout.addWidget(self.upsample_label,0,0)
        self.upsample_layout.addWidget(self.upsample_edit,0,1)
        self.upsample_widget.setLayout(self.upsample_layout)
        
        self.colormaps = ColorMapSelector(settings['cmap'])
        
        
        
        self.init_grid = QtGui.QGridLayout()
        self.param_grid = QtGui.QGridLayout()
        self.graphics_grid = QtGui.QGridLayout()
        
        self.param_grid.addWidget(self.x_min_label,0,0)
        self.param_grid.addWidget(self.x_min_edit,0,1)
        self.param_grid.addWidget(self.x_max_label,1,0)
        self.param_grid.addWidget(self.x_max_edit,1,1)
        self.param_grid.addWidget(self.y_min_label,0,2)
        self.param_grid.addWidget(self.y_min_edit,0,3)
        self.param_grid.addWidget(self.y_max_label,1,2)
        self.param_grid.addWidget(self.y_max_edit,1,3)
        if frac_type == 'Julia':
            self.param_grid.addWidget(self.c_real_label,0,4)
            self.param_grid.addWidget(self.c_real_edit,0,5)
            self.param_grid.addWidget(self.c_imag_label,1,4)
            self.param_grid.addWidget(self.c_imag_edit,1,5)
        
        self.graphics_grid.addWidget(self.graphics_buttons,0,0)
        self.graphics_grid.addWidget(self.colormaps,0,1)
        self.graphics_grid.addWidget(self.upsample_widget,0,2)
        
        self.init_grid.addLayout(self.param_grid,0,0)
        self.init_grid.addLayout(self.graphics_grid,1,0)
        
        self.setLayout(self.init_grid)
        
    def values(self):
        if self.frac == 'Mandelbrot':
            return (self.x_min_edit.text(), self.x_max_edit.text(), 
                    self.y_min_edit.text(), self.y_max_edit.text())
        if self.frac == 'Julia':
            return (self.x_min_edit.text(), self.x_max_edit.text(), 
                    self.y_min_edit.text(), self.y_max_edit.text(),
                    self.c_real_edit.text(), self.c_imag_edit.text())
    
    def graphics_settings(self):
        fast_or_fancy = self.graphics_buttons.selected_button()
        colormap = self.colormaps.selected_colormap()
        upsampling = self.upsample_edit.text()
        return (fast_or_fancy,colormap,upsampling)
    
    def update_defaults(self,settings):
        self.x_min_edit.setText(settings['x_min'])
        self.x_max_edit.setText(settings['x_max'])
        self.y_min_edit.setText(settings['y_min'])
        self.y_max_edit.setText(settings['y_max'])
        try:
            self.c_real_edit.setText(settings['c_real'])
            self.c_imag_edit.setText(settings['c_imag'])
        except:
            pass
        self.graphics_buttons.set_default(settings['fancy_or_fast'])
        
            

class FractalImage(QtGui.QWidget):
    def __init__(self,vals,graphics,width,height,depth=500):
        super(FractalImage,self).__init__()
        
        settings = vals_graphics_to_dict(vals,graphics)
        
        self.last_coords = vals
        
        self.height = height
        self.width = width
        
        self.zoom_button = QtGui.QPushButton("Zoom")
        self.reset_button = QtGui.QPushButton("Reset")
        self.update_frac_button = QtGui.QPushButton('Update From Parameters')
        self.save_button = QtGui.QPushButton("Export Fractal Image")
        
        self.draw_frac(vals,graphics,height,width)
        
        self.main_layout = QtGui.QGridLayout()
        self.image_widget = pg.GraphicsView()
        self.image_data = np.zeros((int(self.height*0.75), int(self.width*0.75),4))
        self.img = pg.ImageItem(rotate(self.image_data,-90))
        self.image_widget.addItem(self.img)
        
        self.roi = pg.ROI((int(self.width*0.1875),int(self.height*0.1875)),
                          (int(self.width*0.375),int(height*0.375)),
                          scaleSnap = True, translateSnap = True, removable = True)
        
        self.roi.sigRemoveRequested.connect(self.test_delete)
        
        self.roi.addScaleHandle((0,0),(0.5,0.5),lockAspect=True)
        
        self.image_widget.addItem(self.roi)
        
        
        self.zoom_button.clicked.connect(self.zoom)
        
        
        self.reset_button.clicked.connect(self.reset)
        
        self.fractal_params = FractalParameters(self.frac_type,settings)
        
        self.update_frac_button.clicked.connect(self.update_frac)
        
        self.save_button.clicked.connect(self.file_save)
        
        
        self.params_widget = QtGui.QWidget()
        self.params_layout = QtGui.QHBoxLayout()
        self.params_layout.addWidget(self.fractal_params)
        self.params_layout.addWidget(self.update_frac_button)
        self.params_widget.setLayout(self.params_layout)
        
        self.main_layout.addWidget(self.image_widget,0,0)
        self.main_layout.addWidget(self.params_widget,1,0)
        self.main_layout.addWidget(self.zoom_button,0,1)
        self.main_layout.addWidget(self.save_button,1,1)
        self.main_layout.addWidget(self.reset_button,0,2)
        
        self.setLayout(self.main_layout)
        
    def test_delete(self):
        print "DID IT WORK"
    
    def file_save(self):
        print "SAVING"
        name = QtGui.QFileDialog.getSaveFileNameAndFilter(self, 'Save File')
        print name[0] + '.png'
        plt.imsave(str(name[0]) + '.png', self.image_data)
        
    def update_frac(self):
        vals = self.fractal_params.values()
        if not type_check(vals):
            self.error_dialog = ErrorDialog('Your X, Y, and C mins and maxes should all numbers.')
            self.error_dialog.exec_()
            return
        if not min_max_check(float(vals[0]),float(vals[1])):
            self.error_dialog = ErrorDialog('Your min real value must be less than your max real value')
            self.error_dialog.exec_()
            return
        if not min_max_check(float(vals[2]), float(vals[3])):
            self.error_dialog = ErrorDialog('Your min imaginary value must be less than your max real value')
            self.error_dialog.exec_()
            return
        graphics = self.fractal_params.graphics_settings()
        if upsampling_check(graphics[2]) == 1:
            self.error_dialog = ErrorDialog('Your upsampling rate must be a number.')
            self.error_dialog.exec_()
            return
        elif upsampling_check(graphics[2]) == 2:
            self.error_dialog = ErrorDialog('Your upsampling rate must be larger than 1.')
            self.error_dialog.exec_()
            return
        
        self.last_coords = vals
        self.draw_frac(vals,graphics,self.height,self.width)
        self.img = pg.ImageItem(rotate(self.image_data,-90))
        self.image_widget.addItem(self.img)
        
    def reset(self):
        graphics = self.fractal_params.graphics_settings()
        if upsampling_check(graphics[2]) == 1:
            self.error_dialog = ErrorDialog('Your upsampling rate must be a number.')
            self.error_dialog.exec_()
            return
        elif upsampling_check(graphics[2]) == 2:
            self.error_dialog = ErrorDialog('Your upsampling rate must be larger than 1.')
            self.error_dialog.exec_()
            return
        vals = self.fractal_params.values()
        if len(vals) == 6:
            vals = (-1.0,1.0,-1.0,1.0,vals[4],vals[5])
        else:
            vals = (-2.0,1.0,-1.0,1.0)
        settings = vals_graphics_to_dict(vals,graphics)
        self.fractal_params.update_defaults(settings)
        self.draw_frac(vals,graphics,self.height, self.width)
    
    
    def zoom(self):
        graphics = self.fractal_params.graphics_settings()
        if upsampling_check(graphics[2]) == 1:
            self.error_dialog = ErrorDialog('Your upsampling rate must be a number.')
            self.error_dialog.exec_()
            return
        elif upsampling_check(graphics[2]) == 2:
            self.error_dialog = ErrorDialog('Your upsampling rate must be larger than 1.')
            self.error_dialog.exec_()
            return
        x_min, y_min = self.roi.pos()
        x_min, y_min = int(x_min), int(y_min)
        x_size, y_size = self.roi.size()
        x_max = x_min + int(x_size)
        y_max = y_min + int(y_size)
        old_coords = (self.last_coords[0],self.last_coords[1],
                      self.last_coords[2],self.last_coords[3])
        new_coords = calculate_new_coords(old_coords,(x_min,x_max,y_min,y_max),
                             self.frac_width, self.frac_height)
        
        
        if len(self.last_coords) == 6:
            new_coords = (new_coords[0], new_coords[1], new_coords[2], 
                          new_coords[3], self.last_coords[4], self.last_coords[5])
        
        settings = vals_graphics_to_dict(new_coords,graphics)
        self.fractal_params.update_defaults(settings)
        self.draw_frac(new_coords,graphics,self.height,self.width)
        
    
    def draw_frac(self,vals,graphics,height,width):
        self.zoom_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.update_frac_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.last_coords = vals
        frac_scale = 0.75
        self.frac_height = int(height*frac_scale)
        self.frac_width = int(width*frac_scale)
        fancy, cmap, upsample = graphics
        if len(vals) == 4:
            self.frac_type = 'Mandelbrot'
            min_x, max_x, min_y, max_y = vals
            c_real, c_imag = None , None

        if len(vals) == 6:
            self.frac_type = 'Julia'
            min_x, max_x, min_y, max_y, c_real, c_imag = vals
        self.thread = FracThread(self,min_x,max_x,min_y,max_y,self.frac_width,
                                 self.frac_height, 512, c_real, c_imag,
                                 upsample, fancy, cmap)
        #self.image_data = create_fractal(min_x, max_x, min_y, max_y,
        #                                    self.frac_width, self.frac_height, 512,
        #                                    c_real, c_imag, upsample, fancy,
        #                                    cmap)
        self.thread.image.connect(self.swap_image)
        self.thread.start()
        
    def swap_image(self,image_data):
        self.image_data = image_data
        self.img = pg.ImageItem(rotate(self.image_data,-90))
        self.image_widget.addItem(self.img)
        self.zoom_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        self.update_frac_button.setEnabled(True)
        self.save_button.setEnabled(True)

      
class FractalWindow(QtGui.QMainWindow):
    def __init__(self,width,height):
        super(FractalWindow,self).__init__()
        
        
        self.screen_width = width
        self.screen_height = height
        
        self.setWindowTitle("Fractal Explorer")
        self.create_select_layout()
        
        self.stacked_layout = QtGui.QStackedLayout()
        self.stacked_layout.addWidget(self.select_fractal_widget)
        
        self.central_widget = QtGui.QWidget()
        self.central_widget.setLayout(self.stacked_layout)
        self.setCentralWidget(self.central_widget)
        
    def create_select_layout(self):
        self.fractal_radio_buttons = RadioButtonWidget("Please Select a Set Type", ["Mandelbrot", "Julia"], "Fractal Type")
        self.submit_type_button = QtGui.QPushButton("Submit")
        self.submit_type_button.clicked.connect(self.init_frac)
        
        self.initial_layout = QtGui.QVBoxLayout()
        self.initial_layout.addWidget(self.fractal_radio_buttons)
        self.initial_layout.addWidget(self.submit_type_button)
        
        self.select_fractal_widget = QtGui.QWidget()
        self.select_fractal_widget.setLayout(self.initial_layout)
        

    def init_frac(self):
        frac_type = self.fractal_radio_buttons.selected_button()
        if frac_type == 0:
            self.fractal_type = 'Mandelbrot'
        if frac_type == 1:
            self.fractal_type = 'Julia'
        
        self.init_widget = QtGui.QWidget()
        
        self.submit_init_button = QtGui.QPushButton('Submit')
        
        self.submit_init_button.clicked.connect(self.submit_init)
        
        self.init_grid = QtGui.QVBoxLayout()
        self.fractal_params = FractalParameters(self.fractal_type)
        self.init_grid.addWidget(self.fractal_params)
        self.init_grid.addWidget(self.submit_init_button)
        
        
        self.init_widget.setLayout(self.init_grid)
        self.stacked_layout.addWidget(self.init_widget)
        self.stacked_layout.setCurrentIndex(1)
        
    def submit_init(self):
        vals = self.fractal_params.values()
        if not type_check(vals):
            self.error_dialog = ErrorDialog('Your Real, Imaginary, and C mins and maxes should all numbers.')
            self.error_dialog.exec_()
            return
        graphics = self.fractal_params.graphics_settings()
        if not min_max_check(float(vals[0]),float(vals[1])):
            self.error_dialog = ErrorDialog('Your min real value must be less than your max real value')
            self.error_dialog.exec_()
            return
        if not min_max_check(float(vals[2]), float(vals[3])):
            self.error_dialog = ErrorDialog('Your min imaginary value must be less than your max real value')
            self.error_dialog.exec_()
            return
        if upsampling_check(graphics[2]) == 1:
            self.error_dialog = ErrorDialog('Your upsampling rate must be a number.')
            self.error_dialog.exec_()
            return
        elif upsampling_check(graphics[2]) == 2:
            self.error_dialog = ErrorDialog('Your upsampling rate must be larger than 1.')
            self.error_dialog.exec_()
            return
        self.stacked_layout.addWidget(FractalImage(vals,graphics,self.screen_width,self.screen_height))
        self.showMaximized()
        self.stacked_layout.setCurrentIndex(2)
        
def get_colormaps():
    cmaps = ['gnuplot2', 'viridis', 'plasma', 'inferno', 'magma',
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper',
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',
            'Pastel1', 'Pastel2', 'Paired', 'Accent',
            'Dark2', 'Set1', 'Set2', 'Set3',
            'tab10', 'tab20', 'tab20b', 'tab20c',
            'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
            'gnuplot', 'CMRmap', 'cubehelix', 'brg', 'hsv',
            'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar']
    return cmaps


def type_check(values):
    for value in values:
        try:
            float(value)
        except:
            return False
    return True

def min_max_check(min_val,max_val):
    return min_val < max_val

def upsampling_check(upsampling):
    try:
        upsampling = float(upsampling)
    except:
        return 1
    if upsampling < 1:
        return 2
    return 0

def vals_graphics_to_dict(vals,graphics):
    settings = {}
    settings['x_min'] = str(vals[0])
    settings['x_max'] = str(vals[1])
    settings['y_min'] = str(vals[2])
    settings['y_max'] = str(vals[3])
    if len(vals) == 6:
        settings['c_real'] = vals[4]
        settings['c_imag'] = vals[5]
    settings['fancy_or_fast'] = graphics[0]
    settings['cmap'] = graphics[1]
    settings['upsample'] = graphics[2]
    
    return settings
def main():
    fractal_explorer = QtGui.QApplication(sys.argv)
    screen_resolution = fractal_explorer.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()
    fractal_window = FractalWindow(width,height)
    fractal_window.show()
    fractal_window.raise_()
    fractal_explorer.exec_()

if __name__ == '__main__':
    main()

#pg.image(create_fractal(-2.0,1.0,-1.0,1.0,700,400,255).T)