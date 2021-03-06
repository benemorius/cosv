import kivy
kivy.require('1.8.0')
  
import serial
from serial.tools import list_ports
from math import sin
from itertools import cycle

from kivy.app import App
from kivy.properties import StringProperty, ObjectProperty, OptionProperty, BoundedNumericProperty
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label 
from kivy.uix.switch import Switch 
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.garden.graph import Graph, MeshLinePlot, LinePlot
from kivy.config import Config
#Config.set('graphics','show_cursor','1')
#Config.write()
#quit()  
def listSerialPorts():
    ports = list_ports.comports()
    portList = list()
    for port in ports:
        portList.append(port.device)
    return portList

class DisplayButton(BoxLayout,Button):
    def updateValue(self,value):
        self.value=value
        self.text=str(self.value).title();
        if (self.value in self.value_colors): self.background_color=self.value_colors.get(self.value) 
        self.dispatch('on_change',self.value)
    def pressEvent(self,*args):
        return True
    def on_change(self,value):
        pass
    def __init__(self,**kwargs):
        self.name=kwargs.pop('name',None)
        self.text_top=kwargs.pop('text_top',' ')
        self.value=kwargs.pop('value',0)
        self.text_bottom=kwargs.pop('text_bottom',' ')
        self.value_colors=kwargs.pop('value_colors',{'default':(1,1,1,1)})
        self.text=str(self.value).title();
        self.register_event_type('on_change')
        if (self.value in self.value_colors): self.background_color=self.value_colors.get(self.value) 
        super(DisplayButton,self).__init__(**kwargs)
        self.spacing=0
        self.bold=True
        self.font_size='20sp'
        self.halign='center'
        self.orientation='vertical'
        labelTop = Label(halign='center',valign='top',text=self.text_top,font_size="13sp")
        self.add_widget(labelTop)
        labelMiddle = Label(text=" ",bold=True,font_size='20sp')
        self.add_widget(labelMiddle)
        labelBottom = Label(halign='center',valign='bottom',text=self.text_bottom,font_size="13sp")
        self.add_widget(labelBottom)
        self.bind(on_release=self.pressEvent)
        #self.bind(value=self.updateValue)

class PopupButton(DisplayButton):
    def __init__(self,**kwargs):
        self.popup_orientation=kwargs.pop('orientation','vertical')
        super(PopupButton,self).__init__(**kwargs)
        self.popupBox=BoxLayout(orientation=self.popup_orientation)
        size_hint=(0.2,0.7)
        if (self.popup_orientation == 'horizontal'): size_hint=(0.7,0.2)
        self.popup=Popup(title=self.text_top,auto_dismiss=False,content=self.popupBox,title_size='20sp',title_align='center',size_hint=size_hint)
    def updateValue(self,value):
        self.popup.dismiss()
        super(PopupButton,self).updateValue(value)
    def pressEvent(self,*args):
        self.popup.pos_hint={'center_x':(self.pos[0]+self.width/2)/Window.width,'bottom_y':(self.pos[1]+self.height)/Window.height}
        self.popup.open()
        super(PopupButton,self).pressEvent(self,*args)

class SliderButton(PopupButton):
    def __init__(self,**kwargs):
        self.min=kwargs.pop('min',0)
        self.max=kwargs.pop('max',100)
        self.step=kwargs.pop('step',1)
        #self.on_update=kwargs.pop('on_update',None)
        self.sliderBind=False
        super(SliderButton,self).__init__(**kwargs)
        self.slider=Slider(min=self.min,value=self.value,max=self.max,step=self.step,cursor_width='32sp',orientation=self.popup_orientation,size_hint=(1,1),size=('25sp','100sp'))
        self.popupBox.add_widget(self.slider)
        #self.popupBox.title=str(self.value)
    def bindTouchUp(self,*args):
        self.slider.bind(on_touch_up=self.updateValue)
    def updateValue(self,instance,event):
        self.value=int(self.slider.value)
        self.slider.unbind(on_touch_up=self.updateValue)
        self.slider.unbind(on_touch_move=self.updatePopup)
        #self.popup.title=str(self.text_top) + str(':  ') + str(self.slider.value)
        super(SliderButton,self).updateValue(self.value)
    def updatePopup(self,*args):
        self.popup.title=str(self.text_top) + str(' : ') + str(self.slider.value)
        Clock.schedule_once(self.bindTouchUp,0.5)
    def pressEvent(self,*args):
        self.slider.value=self.value
        super(SliderButton,self).pressEvent(self,*args)
        self.slider.bind(on_touch_move=self.updatePopup)
        self.updatePopup()

class SelectButton(PopupButton):
    def __init__(self,**kwargs):
        self.values=kwargs.pop('values',('------'))
        super(SelectButton,self).__init__(**kwargs)
        for value in self.values:
            button = Button(text=str(value.title()),size=('100sp','50sp'),on_press=lambda button:self.updateValue(value))
            if value in self.value_colors: 
                button.background_color=self.value_colors.get(value) 
            self.popupBox.add_widget(button)
    def updateValue(self,value):
        super(SelectButton,self).updateValue(value)
    def stopUpdate(self,value):
        return False
    def pressEvent(self,value):
        self.popup.pos_hint={'center_x':(self.pos[0]+self.width/2)/Window.width,'bottom_y':(self.pos[1]+self.height)/Window.height}
        self.popup.open()

class RotaryButton(DisplayButton):
    def __init__(self,**kwargs):
        self.value_colors=kwargs.pop('value_colors',{'default':(1,1,1,1)})
        self.values=kwargs.pop('values',('-----'))
        self.value_list=cycle(self.values)
        super(RotaryButton,self).__init__(**kwargs)
        self.updateValue(self.value)
    def pressEvent(self,*args):
        self.value=next(self.value_list)
        self.updateValue(self.value)
        #super(RotaryButton,self).pressEvent(self,args)
    def updateValue(self,value):
        counter = 0
        if (value in self.values):
            for v in self.value_list:
                counter = counter + 1
                if (v == self.value): break
                if counter >> len(self.values): break
        super(RotaryButton,self).updateValue(value)
class ScrollGraph(Graph):
    def __init__(self,**kwargs):
        self.color=kwargs.pop('color',[1,1,1,1])
        self.line_width=kwargs.pop('line_width',1)
        self.draw_border=True
        self.y_grid_label=True
        self.x_grid_label=False
        self.padding=5
        self.x_grid=True
        self.y_grid=True
        self.xmin=0
        if (not self.y_ticks_major):
            if (self.ymax-self.ymin > 50 ):
                self.y_ticks_major=10
            else:
                self.y_ticks_major=5
        super(ScrollGraph,self).__init__(**kwargs)
        self.plot=LinePlot(color=self.color,line_width=self.line_width)
        self.add_plot(self.plot)
    def add_point(self,point):
        self.plot.points.append(point)
class ScrollGraphBoxLayout(BoxLayout):
    def __init__(self,**kwargs):
        self.graphHistorySize=kwargs.pop('history_size',600000)
        self.graphSize=kwargs.pop('graph_size',1200)
        self.title=kwargs.pop('title',' ')
        super(ScrollGraphBoxLayout,self).__init__(**kwargs)
        self.autoScroll = True
        self.graphPosition = 1
        self.graphDataPosition = 1
        self.graphs = [];
        self.scrollSpeed = 0
        #self.titleBar = Label(text=self.title,size_hint=(1,'10sp'))
        #self.add_widget(self.titleBar)
    def set_title(self,title):
        self.titlebar.text = title	
    def reset(self):
        for graph in self.graphs:
            graph.plot.points = [(0,0)]
        self.graphPosition = 1
        self.graphDataPosition = 1
        self.update()
    def update(self):
        if (self.graphDataPosition == self.graphHistorySize):
            for graph in self.graphs:
                del(graph.plot.points[0])
                graph.plot.points[:] = [(i[0]-1, i[1]) for i in graph.plot.points[:]]
            self.graphDataPosition = self.graphHistorySize - 1;
        if self.autoScroll:
            self.graphPosition = self.graphDataPosition
        #if self.graphPosition > self.graphSize:
        for graph in self.graphs:
            graph.xmin=self.graphPosition-self.graphSize
            graph.xmax=self.graphPosition
    def add_graph(self,graph):
        graph.xmin=0
        graph.xmax=self.graphSize
        self.add_widget(graph)
        self.graphs.append(graph)
    def do_scroll(self,*args):
        self.graphPosition = self.graphPosition + self.scrollSpeed
        if self.graphPosition > self.graphDataPosition:
            self.graphPosition = self.graphDataPosition 
        if self.graphSize < 0.0:
            self.graphPosition = 0.0 
        self.update()  
    def add_points(self,*argv):
        for i,graph in enumerate(self.graphs):
            point = 0.0 if len(argv) < i else argv[i]
            graph.add_point((self.graphDataPosition, point ))
        self.graphDataPosition += 1
        self.update()
    def on_touch_move(self,touch):
        if touch.grab_current is self and 'start_pos' in touch.ud:
            self.scrollSpeed = (touch.x - touch.ud['start_pos'])/4
            self.update()
            return True
        else:
            pass
        super(ScrollGraphBoxLayout,self).on_touch_move(touch)
    def on_touch_down(self,touch):
        touch.grab(self)
        self.autoScroll=False
        touch.ud['start_pos'] = touch.x
        Clock.schedule_interval(self.do_scroll,1/30)
        super(ScrollGraphBoxLayout,self).on_touch_down(touch)
    def on_touch_up(self,touch):
        self.autoScroll=True
        self.scrollSpeed=0
        Clock.unschedule(self.do_scroll)
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        else:
            pass 
        super(ScrollGraphBoxLayout,self).on_touch_up(touch)

class COSVTouchApp(App):
    def build_config(self,config):
        config.setdefaults('state', {
            'running'   : 0,
            'mode'      : 'PCV-VG',
            'tidalv'    : 500,
            'rate'      : 20,
            'ie'        : '1:2',
            'pressure'  : 20,
            'pmax'      : 50,
            'peep'      : 0,
        })
        config.setdefaults('modes', {
            'PCV-VG': 'Pressure Controlled Ventilation'
        })
    def build(self): 
        #availablePorts = listSerialPorts()
        self.serial = serial.Serial()
        self.commandSerial('Q')
        self.enableCO2 = False
        self.tidalVolume=0
        layoutMain = BoxLayout(orientation='horizontal',spacing=0, padding=0)
        
        layoutLeft = BoxLayout(orientation='vertical', spacing=0, padding=0)
        # Graphing area
        self.graphs = ScrollGraphBoxLayout(orientation='vertical', spacing=0, padding=(5,0),history_size=1000,graph_size=1000)
        self.graphs.add_graph(ScrollGraph(ylabel='Paw cmH2O', color=[1, 0, 1, 1], ymin=0, ymax=50))
        self.graphs.add_graph(ScrollGraph(ylabel='Flow L/min', color=[0, 1, 1, 1], ymin=-50, ymax=50,y_ticks_major=20))
        self.graphs.add_graph(ScrollGraph(ylabel='Vt mL', color=[1,1,0,1], ymin=0, ymax=300,size_hint=(1,0.75),y_ticks_major=100))
        if (self.enableCO2):
            self.graphs.add_graph(ScrollGraph(ylabel='CO2 mmHg', color=[0.5,0.5,1,1], ymin=0, ymax=40))
        layoutLeft.add_widget(self.graphs)
        self.graphs.reset()
        
        # Bottom Controls
        layoutControlBottom = BoxLayout(orientation='horizontal', spacing=10, padding=(5,10),size_hint=(1,0.2))
        buttonMode = SelectButton(name='mode',text_top="Mode",value="PCV-VG",values=('PCV-VG','PCV'),text_bottom=" ",on_change=self.commandSerial)
        layoutControlBottom.add_widget(buttonMode);
        
        buttonTidalVolume = SliderButton(name='volume',text_top="TidalV",min=200,max=700,value=500,text_bottom="ml",on_change=self.commandSerial);
        layoutControlBottom.add_widget(buttonTidalVolume);
        
        buttonRespRate = SliderButton(name='rate',text_top="Rate",min=8,max=40,value=18,text_bottom="/min",on_change=self.commandSerial);
        layoutControlBottom.add_widget(buttonRespRate);
        
        buttonInhaleExhale = SelectButton(name='ie',text_top="I:E",value="1:2",values=('1:1','1:2','1:3','1:4'),text_bottom=" ",on_change=self.commandSerial);
        layoutControlBottom.add_widget(buttonInhaleExhale);
        
        #buttonPEEP = SliderButton(name='peep',text_top="PEEP",min=0,value="5",max=25,text_bottom="cmH2O");
        #layoutControlBottom.add_widget(buttonPEEP);
        
        buttonPressureMax = SliderButton(name='pmax',text_top="Pmax",min=10,value="20",max=60,text_bottom="cmH2O",on_change=self.commandSerial);
        layoutControlBottom.add_widget(buttonPressureMax);
        
        layoutLeft.add_widget(layoutControlBottom)
        layoutMain.add_widget(layoutLeft)
        
        # Right Controls
        layoutControlRight = BoxLayout(orientation='vertical', spacing=10, padding=(10,5),size_hint=(0.2,1))
        buttonAlarmPause = SelectButton(name='alarm',text_top='Alarm Status',value="silenced",values={'normal','alarm','silenced'},value_colors={'normal':(0.3,1,0.3,1),'silenced':(1,1,0.3,1),'alarm':(1,0.3,0.3,1)});
        layoutControlRight.add_widget(buttonAlarmPause);
        buttonAlarmSetup = DisplayButton(value="Alarm\nSetup");
        layoutControlRight.add_widget(buttonAlarmSetup);
        buttonSystemSetup = DisplayButton(value="System\nSetup");
        layoutControlRight.add_widget(buttonSystemSetup);
        #self.buttonRun = SelectButton(name='state',text_top="State",on_change=self.runButton,value="stop",values=('stop','run'),value_colors={'stop':(1,0.3,0.3,1),'calibrate':(1,1,0.3,1),'run':(0.3,1,0.3,1)})
        #layoutControlRight.add_widget(self.buttonRun)

        layoutMain.add_widget(layoutControlRight)
        return layoutMain
    def inputSerial(self,instance,value):
        name = instance.name
        self.sendSerial(name,value) 
    def sendSerial(self,name,value):
        try:
            if ! self.serial.is_open:
                availablePorts = listSerialPorts()
                self.serial = serial.Serial(port=availablePorts[0], baudrate=115200,timeout=1)
                Clock.schedule_interval(self.get_data, 1 / 50.)
        except Exception as e:
            popup=Popup(title='Error',content=Label(text=str(e)),size_hint=(None,None),size=(200,200))
            popup.open()
            print('sendSerial exception')
            print(e)
    def get_data(self, dt):
        try:
            if self.serial.is_open:
                while self.serial.in_waiting > 0: 
                    try:
                        row = str(self.serial.readline().decode('ascii')).strip()
                        #print(row)
                        col = row.split(',',10)
                        try:
                            dataType = col[0]
                            if dataType == 'i':
                                print(row)
                            if dataType == 'd':
                                sampleTime = float(col[1])
                                self.graphs.add_points(float(col[2]),float(col[3])*2,float(col[4])*2) #,float(col[2])/float(col[3])*10)
                            else:
                                if dataType == 's':
                                    print(row)
                                    self.run_state = col[1]
                                    self.buttonRun.updateValue(state)
                                if dataType == 'r':
                                    print(row)
                                    self.run_rate = col[1]
                        except Exception as e:
                            print(e)
                    except Exception as e:      
                        print(e)
            else:
                print("Serial connection not open.")
        except Exception as e:
            print(e)
class ErrorPopup(Popup):
    pass
  
if __name__ == '__main__':
    COSVTouchApp().run()
