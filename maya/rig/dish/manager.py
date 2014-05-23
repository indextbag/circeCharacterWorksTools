import sys, os
import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import  inspect
import zipfile
from functools import partial
import json
import uuid
import datetime

if 'dish.data' not in sys.modules.keys():
    frme = inspect.currentframe()
    frameData =  inspect.getframeinfo(frme)
    modulePath = os.path.dirname(frameData[0])
    modulePath = os.path.dirname(modulePath)
    sys.path.append(modulePath)

if 'dishCore' not in sys.modules.keys():
    import dish.core as dishCore    
    reload(dishCore)


author = 'cedric bazillou 2013'
version = 0.01


class UI:
    def __init__(self):
        self.module=''
        self.canvasSize =[430,400]
        self.InfosTab       =  ''
        self.bentoElements  =  ''
        self.gourmetTab     =  ''
        self.dishPrfx       =  ''
        self.pathTxFld      =  ''
        self.dishType       =  ''
        self.dishTabTool    =  ''
        self.IO =  dishCore.IO()
        self.factory = dishCore.factory()
    def widget(self,widgetParent):
        mc.columnLayout( adjustableColumn=True, rs=5 ,p=widgetParent)
        mc.rowLayout(   numberOfColumns=3, 
                        columnWidth2=(80,(self.canvasSize[0]-80-20)),
                        adjustableColumn=2,cl2=('left','both' )  )
        mc.text(l=' Current Path :')
        self.pathTxFld  = mc.textField( 'buildEditor_UI_data_dir_txFld',ed=False  )
        mc.setParent('..')
        mc.separator()
        anchorDock = mc.rowLayout(    numberOfColumns=2,
                                    columnWidth2=(self.canvasSize[0]/5*2+12, 75 ),
                                    adjustableColumn=2,
                                    columnAlign=(1, 'right'),
                                    columnAttach=[(1,'both',0), (2,'both',0)] ,w=self.canvasSize[0])

        self.exposedBentos_UI(anchorDock)
        #------------------------------------------------------------------------------------------------------------
        self.bentosFactory_UI(anchorDock)

        modulePath = ''.join(os.path.dirname(inspect.getfile(self.exposedBentos_UI)))
        mc.textField( self.pathTxFld ,e=True,tx=modulePath)
    def exposedBentos_UI(self,anchor):
        leftPanel = mc.frameLayout( collapsable=False,labelVisible=False, borderStyle='etchedIn',mw=5,mh=5,p=anchor )
        mc.columnLayout( adjustableColumn=True, rs=5 )
        mc.text(l='Available Bentos')
        mc.scrollLayout(	horizontalScrollBarThickness=0,verticalScrollBarThickness=8)
        scrollWdth = mc.columnLayout( adjustableColumn=True, rs=5,w=self.canvasSize[0]/5*2-27,h=self.canvasSize[1]-20)
        dishList = self.IO.exposeZipTemplate()
        
        dishName = ''
        for dish in dishList:
            dishName = os.path.basename(dish).split('.zip')[0]
            btn = mc.button(l=dishName,h=28,ann='test')
            mc.button(btn,e=True,c=partial( self.switch_module, dishName ,dish ))
    def switch_module(self,dishName,dishFile,*args):
        archive = zipfile.ZipFile(dishFile, 'r')
        jsonFile = archive.read('dish.ini')
        jsondata = json.loads(jsonFile)  
        archive.close()

        #Clear chld
        chldrn = mc.layout( self.InfosTab, query=True, childArray=True )
        for chld in chldrn:
            mc.deleteUI(chld)
        #-------------------------------------------------------------------
        mc.columnLayout( adjustableColumn=True ,p=self.InfosTab ,rs=5)        
        header = """<html>
            <body>
            <h1>%s</h1></body>
            </html>
        """%(dishName )
        
        self.dishType  = dishName
        mc.text( self.module,e=True,l=header,font='boldLabelFont')        
        mc.scrollField( editable=False, wordWrap=True, text=jsondata['moduleInfos'] ,h=120)
        mc.separator()   
        LimbMenu = mc.optionMenu( label='Limb type          ' )
        mc.menuItem( label='arm                              ' )
        mc.menuItem( label='leg                              ' )
        mc.menuItem( label='spine                            ' )
        mc.menuItem( label='head                             ' )
        mc.menuItem( label='neck                             ' )
        mc.menuItem( label='foot                             ' )
        mc.menuItem( label='hand                             ' )
        mc.optionMenu( LimbMenu ,e=True,changeCommand=partial(self.composePrfX,LimbMenu))

        
        ArticulationMenu =mc.optionMenu( label='Articulation       ' )    
        mc.menuItem( label='shoulder                        ' )            
        mc.menuItem( label='wrist                           ' )
        mc.menuItem( label='elbow                           ' )
        mc.menuItem( label='finger                          ' )
        mc.menuItem( label='knee                            ' )
        mc.menuItem( label='ankle                           ' )
        mc.optionMenu( ArticulationMenu ,e=True,changeCommand=partial(self.composePrfX,ArticulationMenu))
        
        SideMenu = mc.optionMenu( label='Side                  ' )    
        mc.menuItem( label='left              *l*            ' )            
        mc.menuItem( label='right             *r*            ' )
        mc.menuItem( label='center            *c*            ' )
        mc.optionMenu( SideMenu ,e=True,changeCommand=partial(self.composePrfX,SideMenu))

        self.dishPrfx       =  mc.textField()
        mc.button(l='Import', h=42,c=self.validate_dish_before_merge )        
        
        mc.textScrollList( self.bentoElements , e=True,ra=True)
        self.refresh_dishTabs_contents()
    def validate_dish_before_merge(self,*args):
        prx = mc.textField(  self.dishPrfx ,q=True,tx=True)
        if len(prx)>1:
            path = mc.textField( self.pathTxFld, q=True,tx=True)
            dishFile = os.path.join( path,self.dishType+'.zip')
            self.IO.merge( dishFile,'XX_',prx+'_')
    def composePrfX (self,menuOpt ,*args):
        prx = mc.textField(  self.dishPrfx ,q=True,tx=True)
        module = mc.optionMenu(menuOpt,q=True,value=True).strip()
        if len(prx)<1:
            if '*' in module:
                module = module.split('*')[1]
            mc.textField(  self.dishPrfx ,e=True,tx=module)
        else:
            if '*'  in module:
                module = module.split('*')[1]
            mc.textField(  self.dishPrfx ,e=True,tx=prx+'_'+module )
    def bentosFactory_UI(self,anchor):
        mc.columnLayout( adjustableColumn=True,p=anchor )
        self.module= mc.text( 'CCW_TOOLS_DISHNAME_txFld', l='', h=36  )
        self.dishTabTool = mc.tabLayout( innerMarginWidth=5, innerMarginHeight=5,h=self.canvasSize[1]-84)
        self.InfosTab = mc.frameLayout(   mw=5,labelVisible=False,mh=5,p=self.dishTabTool )
        mc.text(l='')

        
        #--------------------------------------------------------
        mc.frameLayout(  mw=5,labelVisible=False,mh=5,p=self.dishTabTool )
        mc.text(l='')
        
        #--------------------------------------------------------
        self.gourmetTab = mc.frameLayout(  mw=5,labelVisible=False,mh=5,p=self.dishTabTool )
        mc.columnLayout( adjustableColumn=True )
        self.bentoElements =  mc.textScrollList( 'CCW_TOOLS_bentoElements',numberOfRows=18, selectCommand=self.select_installedDish )
        
        
        
        #######################################################################
        
        mc.tabLayout(self.dishTabTool ,e=True,tabLabelIndex=[1,'Infos'])
        mc.tabLayout(self.dishTabTool ,e=True,tabLabelIndex=[2,'Tools'])
        mc.tabLayout(self.dishTabTool ,e=True,tabLabelIndex=[3,'Gourmet Manager'])

        dishList = self.IO.exposeZipTemplate()
        self.switch_module( os.path.basename(dishList[0]).split('.zip')[0],dishList[0] )         
        mc.tabLayout(self.dishTabTool ,e=True,changeCommand=self.refresh_dishTabs_contents)
    def select_installedDish(self,*args):
        dish = mc.textScrollList( 'CCW_TOOLS_bentoElements',q=True,selectItem=True)
        mc.select(dish,r=True)
    def refresh_dishTabs_contents(self,*args):
        currentTab = mc.tabLayout(self.dishTabTool ,q=True,selectTabIndex=True)
        if currentTab == 3:
            dishList = self.factory.collect_similar_dish(self.dishType)
            mc.textScrollList( self.bentoElements ,e=True,ra=True)
            if len(dishList)>0:
                for dish in dishList:
                    mc.textScrollList( self.bentoElements ,e=True,a=dish)