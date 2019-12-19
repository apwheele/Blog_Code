*A set of macros for calculation of various geometries based on origin/destination data.
*Any questions, email apwheele@gmail.com, Andy Wheeler

*Value of Pi.
DEFINE !PI ( )
(4*ARTAN(1))
!ENDDEFINE.

*Converts from Radians to Degrees.
DEFINE !DegToRad (!POSITIONAL !ENCLOSE("(",")"))
(((!1)/180)*!PI)
!ENDDEFINE.

*Converts from Degrees to Radians.
DEFINE !RadToDeg (!POSITIONAL !ENCLOSE("(",")"))
(((!1)/!PI)*180)
!ENDDEFINE.

*Calculates the degree (from due north) given a set of from coordinates and to coordinates.
*From and To take two tokens, x and then y.
DEFINE !DirDeg (Orig = !TOKENS(2)
               /Dest = !TOKENS(2)
               /Out = !TOKENS(1) )
!LET !X1 = !HEAD(!Orig)
!LET !Y1 = !TAIL(!Orig)
!LET !X2 = !HEAD(!Dest)
!LET !Y2 = !TAIL(!Dest)
DO IF !X2 <> !X1.
  COMPUTE #deg = !RadToDeg(ARTAN((!Y2 - !Y1)/(!X2 - !X1))).
ELSE.
  COMPUTE #deg = 0.
END IF.
DO IF !X2 = !X1 AND !Y1 <= !Y2. 
  COMPUTE !Out = 0.
ELSE IF !X2 = !X1 and !Y1 > !Y2.
  COMPUTE !Out = 180.
ELSE IF !X1 > !X2.
  COMPUTE !Out = 270 - #deg.
ELSE IF !X1 < !X2.
  COMPUTE !Out = 90 - #deg.
END IF.
FORMATS !Out (F3.0).
!ENDDEFINE.

*The arctan2 function.
*Takes inputs in radians and returns radians.
DEFINE !ATAN2 (Y = !TOKENS(1)
              /X = !TOKENS(1)
			  /OUT = !TOKENS(1) ) 
DO IF !X > 0.
  COMPUTE !OUT = ARTAN(!Y/!X).
ELSE IF !X < 0 AND !Y >= 0.
  COMPUTE !OUT = ARTAN(!Y/!X) + !PI.
ELSE IF !X < 0 AND !Y < 0.
  COMPUTE !OUT = ARTAN(!Y/!X) - !PI.
ELSE IF !X = 0 AND !Y > 0.  
  COMPUTE !OUT = !PI/2.
ELSE IF !X = 0 AND !Y < 0.
  COMPUTE !OUT = -1*(!PI/2).
END IF.
!ENDDEFINE.

*Computes the distance between two points.
DEFINE !Dist (Orig = !TOKENS(2)
             /Dest = !TOKENS(2)
             /Out = !TOKENS(1) )
COMPUTE !Out = (SQRT((!HEAD(!Orig) - !HEAD(!Dest))**2 + (!TAIL(!Orig) - !TAIL(!Dest))**2)).
!ENDDEFINE.

*to calculate new x y given seed, orientation(in radians), and distance.
DEFINE !Move (Orig = !TOKENS(2)
             /Orient = !TOKENS(1)
             /Dist = !TOKENS(1) 
             /Out = !TOKENS(2) )
COMPUTE !HEAD(!Out) = !HEAD(!Orig) + SIN(!Orient)*!Dist.
COMPUTE !TAIL(!Out) = !TAIL(!Orig) + COS(!Orient)*!Dist.
!ENDDEFINE.

*Quadratic bezier curve between two points given a control point.
DEFINE !QuadBez (Orig = !TOKENS(2)
                /Dest = !TOKENS(2)
                /Cont = !TOKENS(2)
                /Dens = !DEFAULT(15) !TOKENS(1)
                /Out = !TOKENS(1) )
!LET !origin_x = !HEAD(!Orig)
!LET !origin_y = !TAIL(!Orig)
!LET !control_x = !HEAD(!Cont)
!LET !control_y = !TAIL(!Cont)
!LET !dest_x = !HEAD(!Dest)
!LET !dest_y = !TAIL(!Dest)
!LET !OutX = !CONCAT(!Out,"_x")
!LET !OutY = !CONCAT(!Out,"_y")
VECTOR !OutX(!Dens).
VECTOR !OutY(!Dens).
LOOP #i = 1 to !Dens.
  COMPUTE #t = #i/(!Dens+1).
  COMPUTE !OutX(#i) = ((1-#t)**2)*!origin_x + (2*(1-#t)*#t*!control_x) + ((#t**2)*!dest_x).
  COMPUTE !OutY(#i) = ((1-#t)**2)*!origin_y + (2*(1-#t)*#t*!control_y) + ((#t**2)*!dest_y).
END LOOP.
!ENDDEFINE.

*******************************************************************.
*Some examples of use.
 * DATA LIST FREE / ID X1 Y1 X2 Y2.
 * BEGIN DATA
1 1 3 2 2
2 5 2 3 4
3 1 1 2 1
4 4 1 3 1
5 1 4 1 5
6 2 5 2 4
END DATA.
 * FORMATS ALL (F1.0).
 * VARIABLE LEVEL ID (NOMINAL) X1 TO Y2 (SCALE). 
 * DATASET NAME Test.

*Plot of the directions.
 * GGRAPH
  /GRAPHDATASET NAME="graphdataset" VARIABLES=X1 Y1 X2 Y2 ID
  /GRAPHSPEC SOURCE=INLINE.
 * BEGIN GPL
  SOURCE: s=userSource(id("graphdataset"))
  DATA: X1=col(source(s), name("X1"))
  DATA: Y1=col(source(s), name("Y1"))
  DATA: X2=col(source(s), name("X2"))
  DATA: Y2=col(source(s), name("Y2"))
  DATA: ID=col(source(s), name("ID"), unit.category())
  GUIDE: axis(dim(1), label("X"))
  GUIDE: axis(dim(2), label("Y"))
  SCALE: linear(dim(1), min(0), max(6))
  SCALE: linear(dim(2), min(0), max(6))
  ELEMENT: edge(position((X1*Y1)+(X2*Y2)), shape(shape.arrow))
  ELEMENT: point(position(X1*Y1), color.interior(color.black), label(ID))
END GPL.

*Direction in degrees from due north.
 * /*!DirDeg Orig = X1 Y1 Dest = X2 Y2 Out = Degrees.*/
EXECUTE.

*Convert to radians.
 * /*COMPUTE Radians = !DegToRad(Degrees).*/
/*COMPUTE Degrees2 = !RadToDeg(Radians).*/
EXECUTE.

*Distance between the two points.
 * /*!Dist Orig = X1 Y1 Dest = X2 Y2 Out = Distance.*/
EXECUTE.

*Creating a set of control points given origin, distance and direction (in radians).
 * COMPUTE #or = !DegToRad(Degrees2+90).
*Mid point.
 * COMPUTE #dis = Distance/2.
 * /*!Move Orig = X1 Y1 Orient = Radians Dist = #dis Out = MidX MidY.*/
*Control point perpindicular to midpoint at half the distance.
 * COMPUTE #or = !DegToRad(Degrees2-90).
 * /*!Move Orig = MidX MidY Orient = #or Dist = #dis Out = ControlX ControlY.*/
FORMATS MidX MidY ControlX ControlY (F1.0).
 * EXECUTE.

*Plotting control points.
 * GGRAPH
  /GRAPHDATASET NAME="graphdataset" VARIABLES=X1 Y1 X2 Y2 ID ControlX ControlY
  /GRAPHSPEC SOURCE=INLINE.
 * BEGIN GPL
  SOURCE: s=userSource(id("graphdataset"))
  DATA: X1=col(source(s), name("X1"))
  DATA: Y1=col(source(s), name("Y1"))
  DATA: X2=col(source(s), name("X2"))
  DATA: Y2=col(source(s), name("Y2"))
  DATA: ID=col(source(s), name("ID"), unit.category())
  DATA: ControlX=col(source(s), name("ControlX"))
  DATA: ControlY=col(source(s), name("ControlY"))
  GUIDE: axis(dim(1), label("X"))
  GUIDE: axis(dim(2), label("Y"))
  SCALE: linear(dim(1), min(0), max(6))
  SCALE: linear(dim(2), min(0), max(6))
  ELEMENT: edge(position((X1*Y1)+(X2*Y2)), shape(shape.arrow))
  ELEMENT: point(position(X1*Y1), color.interior(color.black), label(ID))
  ELEMENT: point(position(ControlX*ControlY), color.interior(color.green))
END GPL.

*Creating Bezier curves - then reshaping to plot.
 * /*!QuadBez Orig = X1 Y1 Dest = X2 Y2 Cont = ControlX ControlY Dens = 15 Out = Bez.*/
EXECUTE.
 * VARSTOCASES
  /MAKE X FROM X1 Bez_x1 TO Bez_x15 X2
  /MAKE Y FROM Y1 Bez_y1 TO Bez_y15 Y2
  /INDEX Type
  /DROP Radians Degrees2 Distance MidX MidY ControlX ControlY.
 * RECODE Type (1 = 1)(2 THRU 16 = 2)(17 = 3).
 * VALUE LABELS Type
  1 'Origin'
  2 'Bezier'
  3 'Destination'.

 * GGRAPH
  /GRAPHDATASET NAME="graphdataset" VARIABLES=X Y ID Type
  /GRAPHSPEC SOURCE=INLINE.
 * BEGIN GPL
  SOURCE: s=userSource(id("graphdataset"))
  DATA: X=col(source(s), name("X"))
  DATA: Y=col(source(s), name("Y"))
  DATA: ID=col(source(s), name("ID"), unit.category())
  DATA: Type=col(source(s), name("Type"), unit.category())
  GUIDE: axis(dim(1), label("X"))
  GUIDE: axis(dim(2), label("Y"))
  SCALE: linear(dim(1), min(0), max(6))
  SCALE: linear(dim(2), min(0), max(6))
  ELEMENT: path(position(X*Y), split(ID))
  ELEMENT: point(position(X*Y), color.interior(Type), size(size."4"))
END GPL.

*Making order of arrows.
 * DO IF ID = LAG(ID).
 *   COMPUTE XO = LAG(X).
 *   COMPUTE YO = LAG(Y).
 * END IF.

 * GGRAPH
  /GRAPHDATASET NAME="graphdataset" VARIABLES=X Y XO YO ID Type MISSING=VARIABLEWISE
  /GRAPHSPEC SOURCE=INLINE.
 * BEGIN GPL
  SOURCE: s=userSource(id("graphdataset"))
  DATA: X=col(source(s), name("X"))
  DATA: Y=col(source(s), name("Y"))
  DATA: XO=col(source(s), name("XO"))
  DATA: YO=col(source(s), name("YO"))
  DATA: ID=col(source(s), name("ID"), unit.category())
  DATA: Type=col(source(s), name("Type"), unit.category())
  GUIDE: axis(dim(1), label("X"))
  GUIDE: axis(dim(2), label("Y"))
  SCALE: linear(dim(1), min(0), max(6))
  SCALE: linear(dim(2), min(0), max(6))
  ELEMENT: edge(position((XO*YO)+(X*Y)), split(ID), shape(shape.arrow))
END GPL.

*To make continuous circular ramps you can map color to half direction.
*And transparency (or saturation) to abs value of degrees.
 * DATASET CLOSE ALL.
 * INPUT PROGRAM.
 * COMPUTE #dens = 360.
 * LOOP #i = 1 TO #dens.
 *   COMPUTE Deg = (#i-1)*(360/#dens).
 *   END CASE.
 * END LOOP.
 * END FILE.
 * END INPUT PROGRAM.
 * DATASET NAME Circ.

 * /*COMPUTE #or = !DegToRad(Deg).*
 * /*!Move Orig = 0 0 Orient = #or Dist = 1 Out = LocX LocY.*/
 * COMPUTE Col = (Deg >= 180).
 * DO IF Deg >= 180.
 *   COMPUTE Sat = ABS(180-Deg).
 * ELSE.
 *   COMPUTE Sat = ABS(Deg-180).
 * END IF.
 * FORMATS Sat (F3.0) Col (F1.0). 
 * EXECUTE.

 * GGRAPH
  /GRAPHDATASET NAME="graphdataset" VARIABLES=LocX LocY Sat Col
  /GRAPHSPEC SOURCE=INLINE.
 * BEGIN GPL
  PAGE: begin(scale(500px,500px))
  SOURCE: s=userSource(id("graphdataset"))
  DATA: LocX=col(source(s), name("LocX"))
  DATA: LocY=col(source(s), name("LocY"))
  DATA: Sat=col(source(s), name("Sat"))
  DATA: Col=col(source(s), name("Col"), unit.category())
  TRANS: base=eval(0)
  GUIDE: axis(dim(1), null())
  GUIDE: axis(dim(2), null())
  GUIDE: legend(aesthetic(aesthetic.color), null())
  GUIDE: legend(aesthetic(aesthetic.color.saturation), null())
  GUIDE: legend(aesthetic(aesthetic.transparency), null())
  COORD: rect(dim(1,2), sameRatio())
  SCALE: linear(dim(1), min(-1), max(1))
  SCALE: linear(dim(2), min(-1.05), max(.96))
  SCALE: cat(aesthetic(aesthetic.color), map(("0",color.green),("1",color.purple)))
  SCALE: linear(aesthetic(aesthetic.color.saturation), aestheticMinimum(color.saturation."0"), 
         aestheticMaximum(color.saturation."0.8"), min(0), max(180))
  SCALE: linear(aesthetic(aesthetic.transparency), aestheticMinimum(transparency."0"), 
         aestheticMaximum(transparency."0.97"), min(0), max(180))
  ELEMENT: edge(position((base*base)+(LocX*LocY)), color.saturation(Sat), color(Col), 
           size(size."4"), transparency(Sat))
  PAGE: end()
END GPL.
*******************************************************************.
