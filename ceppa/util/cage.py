# THIS IS INTENDED TO SUPERCEDE defineShapeOfEnclosure.py -- the cage is an object
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class Cage():
    def __init__(self, PRINTOUT=False):
        if PRINTOUT:
            print "loading Cage specs.."
        self.xNovelObject=3.75
        self.yNovelObject=22.5
        self.nearnessRadius=7.0
        # locations
        # sleeping is used in backwardfix
        self.mouseCMXSleeping = -13.25 #old alan/darren value
        self.mouseCMYSleeping = 38.0 #old 
        # self.mouseCMXSleeping= -10. # corrected by xy_plots 
        # self.mouseCMYSleeping=36.5 
        # this is some point close to the center of available space in the niche
        self.mouseCMXAtNest= -13.25 + 4.25 #larry
        self.mouseCMYAtNest = 38.0 -1.15
        self.mouseCMXAtPhoto = -12.75 #the Alan opinion
        self.mouseCMYAtPhoto = 0.4 #old alan/darren
        # self.mouseCMXAtPhoto=-13.75 # corrected by xy_plots 
        # self.mouseCMYAtPhoto=3.0 
        self.mouseCMXAtLick = 0.0
        self.mouseCMYAtLick = 3.0
        self.mouseCMXDoorway = -8.25 -1.2 # after Larry's
        self.mouseCMYDoorway = 35.0 + 1.2  #
        # # # #CHEKC THIS!!!!!
        self.enclosureMidX = -6.25
        self.enclosureMidY = 22.0
        # boundaries
        self.CMYLower = 1.0
        self.CMXUpper = 3.75
        self.CMXLower = -16.25
        # nest xs
        self.nestLeftX = self.CMXLower+3.0
        self.nestRightX = -6.25 + 1.2 #observational. + 1.2cm after Larry's observation (May 2015)
        self.nestBottomXMax = -8.75 #observational
        self.CMYUpper = 43.0
        # nest ys
        self.nestTopY = self.CMYUpper-3.0 #-4.0 observational, -3.0 after Larry's
        self.nestRightYMin = 35.5 #observational
        self.nestBottomY = 33 - 1.2 #observational - 1.2cm after Larry's
        # any figure of the cage you want to plot
        self.pictureXMin = self.CMXLower
        self.pictureXMax = self.CMXUpper
        self.pictureYMin = 0                # cage bottom at feeder (CMYLower-1)
        self.pictureYMax = self.CMYUpper
        self.enclosurePenaltyLowerBoundXMin = -10.5     # cage bottom at lickometer, at Y = self.CMYLower
        self.enclosurePenaltyLowerBoundXMax = 3.75 
        # # center_cage rectangle: following Larry's drawing, niche is about 12x9
        self.xr_lower = self.CMXLower + 7
        self.xr_upper = self.CMXUpper - 7
        self.yr_lower = self.CMYLower + 12
        self.yr_upper = self.CMYLower + 31  
        # mouse detection coordinates xy at lick, feed, nest
        self.xy_l = [self.mouseCMXAtLick, self.mouseCMYAtLick] 
        self.xy_p = [self.mouseCMXAtPhoto, self.mouseCMYAtPhoto + 0.6] # Larry
        self.xy_n = [self.mouseCMXAtNest, self.mouseCMYAtNest]
        # origin at cage bottom at lickometer
        self.xy_o = [self.mouseCMXAtLick, self.CMYLower]    
        # distances from origin
        self.to_l = np.sqrt((self.xy_l[0] - self.xy_o[0])**2 + (self.xy_l[1] - self.xy_o[1])**2)
        self.to_p = np.sqrt((self.xy_p[0] - self.xy_o[0])**2 + (self.xy_p[1] - self.xy_o[1])**2)
        self.to_n = np.sqrt((self.xy_n[0] - self.xy_o[0])**2 + (self.xy_n[1] - self.xy_o[1])**2)
        # four corners coordinates
        self.xy_topleft = [self.CMXLower, self.CMYUpper]
        self.xy_botleft = [self.CMXLower, 0]    # cage bottom at feeder
        self.xy_botright = [self.CMXUpper, 0]
        self.xy_topright = [self.CMXUpper, self.CMYUpper]
        # cage size
        self.dx = self.CMXUpper - self.CMXLower
        self.dy = self.CMYUpper - self.CMYLower
        if PRINTOUT:
            print "mouse xy coordinates at locations and distances from origin (at lickometer device)",  self.xy_o
            print "lick %s\ndistance_to_origin=%1.2f" %(self.xy_l, self.to_l)
            print "photo %s\ndist=%1.2f" %(self.xy_p, self.to_p)
            print "nest %s\ndist=%1.2f" %(self.xy_n, self.to_n)

            print "(outer) cage corners:"
            print "xy_topleft ", self.xy_topleft
            print "xy_botleft ", self.xy_botleft
            print "xy_botright ", self.xy_botright
            print "xy_topright ", self.xy_topright

            print "cage size: %1.2f x %1.2f cm2" %(self.dx, self.dy)


    def draw_enclosure(self, ax, lw=2., color='k', NICHE=True, DENS=False, SHORTEN=False, rightCircle=False, leftCircle=False):
        """ draw enclosure
            default. draw complete niche real thing
            cage boundary only: NICHE = False
                DENS = True # move walls to match 12x24 grid in position density
                SHORTEN = True # shorten walls for xy path plots
        """
        # draw Niche
        if NICHE:
            shift_l = 0.    # Niche right shift left
            shift_u = 0.    # Niche bottom shift up
            if DENS:     # shift walls to match 12x24grid for position density
                shift_l = -0.2#1    # shift left
                shift_u = -0.4#0.7  
            short_r = 0     # Niche right shorten
            short_b = 0     # Niche bottom shorten
            if SHORTEN:
                short_r = 1.8   
                short_b = 2 

            ax.plot((self.nestRightX - shift_l, self.nestRightX - shift_l), (self.nestRightYMin + short_r, self.pictureYMax-1.), 
                color=color, lw=2.5) # nest right side
            ax.plot((self.CMXLower+1., self.nestBottomXMax - short_b), (self.nestBottomY + shift_u, self.nestBottomY + shift_u), 
                color=color, lw=2.5) # nest bottom
            # Niche top-left dead space. not needed in DENS
            if not DENS:
                ax.plot((self.nestLeftX, self.nestRightX), (self.nestTopY, self.nestTopY), color=color, lw=lw) # nest top side
                ax.plot((self.nestLeftX, self.nestLeftX), (self.nestBottomY, self.nestTopY), color=color, lw=lw) # nest left side
        
                # # Niche grey square
                # width = (self.nestRightX - shift_l) - self.nestLeftX
                # height = self.nestTopY - (self.nestBottomY + shift_u)

                # niche_bottom_left = (self.nestLeftX, self.nestTopY - height)
                # niche = patches.Rectangle(niche_bottom_left, width, height, 
                #   facecolor="0.85", edgecolor="0.85", zorder=0
                #   )

                # ax.add_patch(niche)
        # novel object
        if rightCircle:
            circleWYES = np.linspace(self.yNovelObject-self.nearnessRadius, self.yNovelObject+self.nearnessRadius,1000)
            circleEXES = self.xNovelObject-np.sqrt(self.nearnessRadius**2-(circleWYES-self.yNovelObject)**2)
            ax.plot(circleEXES,circleWYES, '-', color='purple', lw=0.5)

        if leftCircle:
            circleWYES = np.linspace(self.yLeftNovelObject-self.nearnessRadius, self.yLeftNovelObject+self.nearnessRadius,1000)
            circleEXES = self.xLeftNovelObject+np.sqrt(self.nearnessRadius**2-(circleWYES-self.yLeftNovelObject)**2)
            ax.plot(circleEXES,circleWYES, '-', color='purple', lw=0.5)



    # def map_rect4x2_to_cage_coordinates(self, rect):
        
    #     xl, xr, yb, yt = self.CMXLower, self.CMXUpper, self.CMYLower, self.CMYUpper 

    #     dx = (xr - xl) / 2.

    #     x1 = xl + dx

    #     dy = (yt - yb) / 4.

    #     y1, y2, y3 = [yb + k*dy for k in range(1, 4)]

    #     a, b = rect#.tolist()
        
    #     x, y = xl, y3
    #     if a == 1:
    #         y = y2
    #     elif a == 2:
    #         y = y1
    #     elif a == 3:
    #         y = yb
            
    #     if b == 1:
    #         x = x1 

    #     return (x, y), dx, dy         # cell lower left, width, height


    # def plot_cage_geometry(self, ax=None, fontsize=None, NEST=True):
    #     """
    #     """

    #     print "plotting HCM cage geometry.."

    #     colors = ['0.3', 
    #         '#CC6600',      # 1 feed: orange
    #         '#00008B',      # 2 drink
    #         ]

    #     matplotlib.rcParams['font.size'] = 16.0
    #     fontsize = 20
    #     figsize = (4, 6)
    #     fig, ax = plt.subplots(figsize=figsize)

    #     self.draw_enclosure(ax=ax)

    #     self.draw_device_labels(ax=ax, colors=colors, fontsize=24, NEST=NEST)

    #     self.draw_dist_lines_and_text(ax=ax, colors=colors)

    #     # self.draw_mouse_locations(ax=ax, colors=colors)

    #     fname = '/data/Experiments/SS_Data_051905_FV/HCM_cage.pdf'
    #     plt.savefig(fname)
    #     plt.close()
    #     print "saved to:\n%s" %fname


    # def draw_device_labels_(self, ax, fontsize=12, labelpad=-2, NEST=False):
        
    #   colors = ['k', '#FA9531', '#1F75FE']
    #   ax.text(self.mouseCMXAtPhoto - 1., self.CMYLower - 4 + labelpad, 'F', 
    #       fontsize=fontsize,
    #       color=colors[1],
    #       ha='center'
    #       )           
    #   ax.text(self.mouseCMXAtLick - 1., self.CMYLower - 4 + labelpad, 'W', 
    #       fontsize=fontsize, 
    #       color=colors[2],
    #       ha='center'
    #       )
    #   if NEST:
    #       ax.text(-12, 36, 'N', color=colors[0], fontsize=fontsize)

    # def draw_dist_lines_and_text(self, ax, fontsize=None):
    #     """draw lines connecting notorious locations to origin in cage
    #         show plot_distance_to_nest
    #         this is a kind of qualitative picture of what is going on with locations and distances
    #     """

    #     colors = ['k', '#FA9531', '#1F75FE']

    #     ax.autoscale(False)


    #     # # nest
    #     x = [self.xy_o[0], self.xy_n[0]]    
    #     y = [self.xy_o[1], self.xy_n[1]]
    #     text = '%1.1fcm' %self.to_n     

    #     ax.plot(x, y, '--', lw=2., color=colors[0], zorder=2)
    #     ax.text(-10, 18, text, 
    #         fontsize=fontsize,
    #         ha='center',
    #         color=colors[0]
    #         )
        
    #     # photo
    #     x = [self.xy_o[0], self.xy_p[0]] 
    #     y = [self.xy_o[1]+0.9, self.xy_p[1]+0.9]
    #     text = '%1.1fcm' %self.to_p

    #     ax.plot(x, y, '--', lw=2., color='k', zorder=2)
    #     ax.scatter(x[1], y[1]-0.5, marker='o', s=50., color=colors[1]) 
    #     ax.text(-6, 2.7, text, 
    #         fontsize=fontsize,
    #         ha='center',
    #         color='k'
    #         )

    #     # lick
    #     x = [self.xy_o[0], self.xy_l[0]]    
    #     y = [self.xy_o[1], self.xy_l[1]]
    #     text = '%1.1fcm' %self.to_l
    #     ax.scatter(x[0], y[0], marker='o', s=50., color=colors[2]) # larry's
    #     # ax.plot(x, y, '--', linewidth=2., color=colors[2])
    #     # ax.scatter(x[1], y[1], marker='o', s=50., color=colors[2])
    #     # ax.text(1, 2, text, fontsize=fontsize, color=colors[2])


    #     # origin
    #     # ax.scatter(x[0], y[0], marker='o', s=150., color='k') 

    #     # # size
    #     # text1 = '%1.1f cm' %self.dy
    #     # text2 = '%1.1f cm' %self.dx
    #     # ax.text(self.pictureXMax+4, self.pictureYMax-20, text1, fontsize=fontsize, rotation=270)
    #     # ax.text(self.pictureXMin+6, self.pictureYMax+2, text2, fontsize=fontsize)
    #     # ax.annotate('', (0, 1.04), (1, 1.04), xycoords='axes fraction', arrowprops={'arrowstyle':'<->'})
    #     # ax.annotate('', (1.15, 1), (1.15, 0), xycoords='axes fraction', arrowprops={'arrowstyle':'<->'})
        



    # def draw_mouse_locations(self, ax, colors, SHOW=False):
    #     """draw mouse notorious locations
    #     """
    #     # # these were mouse locations
    #     R = 1.5
    #     npatch = patches.Circle(tuple(self.xy_n), R, color=colors[0], alpha=0.5, zorder=1)  #nest
    #     ppatch = patches.Circle(tuple(self.xy_p), R, color=colors[1], alpha=0.3, zorder=1)  #photobeam
    #     lpatch = patches.Circle(tuple(self.xy_l), R, color=colors[2], alpha=0.3, zorder=1)  #lickometer
    #     ax.add_patch(npatch)
    #     ax.add_patch(ppatch)
    #     ax.add_patch(lpatch)

    #     if SHOW:
    #         # doorway
    #         ax.scatter(self.mouseCMXDoorway, self.mouseCMYDoorway, marker='x', s=50, color='k') # supposed narrowest passage
    #         ax.text(self.mouseCMXDoorway+1, self.mouseCMYDoorway-2, 'doorway')
    #         # middle of the cage
    #         ax.scatter(self.enclosureMidX, self.enclosureMidY, marker='+', s=50, color='k')
    #         ax.text(self.enclosureMidX+1, self.enclosureMidY-1, 'midxy')
    #         # # nest diagonal
    #         # ax.plot((self.nestRightX, self.CMXLower), (self.nestBottomY, self.CMYUpper), color=color) # nest runway
    #         # mouse positions at devices
    #         # ax.plot(self.mouseCMXAtLick, self.mouseCMYAtLick, 'o', color='blue', markeredgewidth=0, ms=10) # supposed LickCM
    #         # ax.plot(self.mouseCMXAtPhoto,self.mouseCMYAtPhoto,'o', color='orange', markeredgewidth=0, ms=10)      
            



