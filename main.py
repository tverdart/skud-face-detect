from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import time
import os
import sys
import face_recognition


Builder.load_string("""
<CameraClick>:
    orientation: 'vertical'
    Camera:
        id: camera
        play: True
        index: 0
        resolution: (640, 480)
        pos_hint: {'y': 0.078}

    BoxLayout:
        orientation: 'vertical'

        Button:
            text: 'Capture'
            size_hint_y: None
            height: '48dp'
            on_press: root.capture()

        Button:
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'
            height: '48dp'
            size_hint_y: None

<MenuScreen>:
    BoxLayout:
        Button:
            text: 'Goto registration'
            on_press:
                root.manager.current = 'cam'
                root.change_flag('registration')
        Button:
            text: 'Goto recognition'
            on_press:
                root.manager.current = 'cam'
                root.change_flag('recognition')
        Button:
            text: 'Quit'
            on_press: root.ext()
""")

def all_indices(value, qlist):
    indices = []
    idx = -1
    while True:
        try:
            idx = qlist.index(value, idx+1)
            indices.append(idx)
        except ValueError:
            break
    if (indices[0]==1):
        return "Гундарев Арсентий Сергеевич"
    elif (indices[0]==0):
        return "Твердохлебов Артём Сергеевич"
    elif (indices[0]==2):
        return ""
    elif (indices[0]==3):
        return ""
    elif (indices[0]==4):
        return ""
    else:
        return indices


class MenuScreen(Screen):
    def change_flag(self, param):
        CameraClick.flag = param

    def ext(self):
        sys.exit()


class CameraClick(Screen):
    flag = ''

    

    def capture(self):
        
        #сохранение фоток с использованием текущего времени в качестве названия
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        camera.export_to_png("IMG_{}.png".format(timestr))
        os.rename("IMG_{}.png".format(timestr), 'Faces_1/' + "IMG_{}.png".format(timestr))

        results = []
        files = os.listdir('Faces_1') #создает список файлов в папке Faces_1

        if(self.flag == 'registration'):
            #создание всплывающего окна с текстом 'Вы зарегистрировались!'
            popup = Popup(content=Label(text="Вы зарегистрировались!"), size_hint=(.6, .6), title="Итог работы")
            popup.open()
        elif(self.flag == 'recognition'):
            face1 = face_recognition.load_image_file('Faces_1/' + "IMG_{}.png".format(timestr)) #загрузка только что созданной фотки

            os.remove('Faces_1/' + "IMG_{}.png".format(timestr)) #удаление фотки, созданной для распознавания

            desc_face1 = face_recognition.face_encodings(face1) #извлечение дескрипторов лиц из этой фотки в список

            if(len(desc_face1) == 0): #если список дескрипторов лиц пуст
                #создание всплывающего окна с текстом 'Не получилось извлечь дескриптор :('
                popup = Popup(content=Label(text="Не получилось извлечь дескриптор :("), size_hint=(.6, .6), title="Итог работы")
                popup.open()
                sys.exit()
            else: #если не пуст, тогда перезапись в переменную desc_face1 дескриптора ближайшего лица, а не всего списка
                desc_face1 = desc_face1[0]

                del files[files.index("IMG_{}.png".format(timestr))] #удаление из списка файлов фотки для распознавания,
                                                                     #чтобы не происходило сравнение этого дескриптора с самим собой
                for f in files:
                    face2 = face_recognition.load_image_file('Faces_1/' + f) #загрузка ранее созданных фотографий для сравнения
                    if len(face_recognition.face_encodings(face2)) == 0:
                        results.append('exception')
                    else:
                        desc_face2 = face_recognition.face_encodings(face2)[0] #извлечение дескриптора из ближайшего к камере лица на
                                                                               #фотографии
                        result = face_recognition.compare_faces([desc_face2], desc_face1)[0] #сравнение дескрипторов (первый аргумент - список,
                                                                                             #потому что второй аргумент сравнивается с каждым
                                                                                             #элементом списка; [0] - так как возвращается
                                                                                             #список результатов сравнения,
                                                                                             #а нам нужен первый и единственный элемент)
                        results.append(result)

                if(results.count(True) > 0): #если хотя бы один результат сравнения равен True, то
                    #создание всплывающего окна с текстом 'Мы вас узнали! :)'
                    popup = Popup(content=Label(text=("Доступ разрешён: "+ str(all_indices(True, results)))), size_hint=(.6, .6), title="Итог работы")
                    popup.open()
                else:
                    #создание всплывающего окна с текстом 'Мы вас не узнали :('
                    popup = Popup(content=Label(text="Доступ запрещён: лицо не распознано"), size_hint=(.6, .6), title="Итог работы")
                    popup.open()


sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(CameraClick(name='cam'))


class TestApp(App):
    def build(self):
        return sm


if __name__ == '__main__': #запуск приложения
    TestApp().run()
