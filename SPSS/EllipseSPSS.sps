
*X and Y refer to the center of the ellipse.
*Major and Minor refer to the sizes of the axis.
*Angle refers to the slope of axis in degrees.
*Steps refers to the number of locations around the ellipse that are calculated - defaults to 36.
*Adapted from wikipedia - http://en.wikipedia.org/w/index.php?title=Ellipse&oldid=456212176#Ellipses_in_computer_graphics.

DEFINE !Ellipse (X = !TOKENS(1)
                /Y = !TOKENS(1)
                /Major = !TOKENS(1)
                /Minor = !TOKENS(1)
                /Angle = !TOKENS(1) 
                /Steps = !DEFAULT(36) !TOKENS(1) 
                /Id = !DEFAULT($casenum) !TOKENS(1) )
dataset copy Ellipse.
dataset activate Ellipse.
compute Major = !Major.
compute Minor = !Minor.
compute Angle = !Angle.
compute X = !X.
compute Y = !Y.
compute Id = !Id.
match files file = *
/keep X Y Major Minor Angle Id.
compute #Pi = 4*ARTAN(1).
compute #beta = -Angle*(#Pi/180).
compute #sinbeta = SIN(#beta).
compute #cosbeta = COS(#beta).
compute #Step = 360/!Steps.
vector StepX(!Steps).
vector StepY(!Steps).
loop #i = 1 to (!Steps).
  compute #alpha = ((#i-1)*#Step)*(#Pi/180).
  compute #sinalpha = SIN(#alpha).
  compute #cosalpha = COS(#alpha).
  compute StepX(#i) = X + (Major*#cosalpha*#cosbeta - Minor*#sinalpha*#sinbeta).
  compute StepY(#i) = Y + (Major*#cosalpha*#sinbeta + Minor*#sinalpha*#cosbeta).
end loop.
varstocases
/MAKE X from StepX1 to !CONCAT("StepX",!Steps)
/MAKE Y from StepY1 to !CONCAT("StepY",!Steps)
/KEEP Id.
!ENDDEFINE.

*Example use case.
dataset close all.
set seed 10.
input program.
loop #i = 1 to 10.
  compute Ox = RV.UNIFORM(3,7).
  compute Oy = RV.UNIFORM(3,7).
  compute OMaj = RV.UNIFORM(3,6).
  compute OMin = RV.UNIFORM(0,2).
  compute OAng = RV.UNIFORM(30,150).
  end case.
end loop.
end file.
end input program.
dataset name test.
exe.
output close all.
*SET MPRINT ON.
!Ellipse X = Ox Y = Oy Major = OMaj Minor = OMin Angle = OAng Steps = 100.
*SET MPRINT OFF.

*Plots only the edges.
GGRAPH
  /GRAPHDATASET NAME="graphdataset" VARIABLES=X Y Id
  REPORTMISSING=NO
  /GRAPHSPEC SOURCE=INLINE.
BEGIN GPL
 SOURCE: s=userSource(id("graphdataset"))
 DATA: X=col(source(s), name("X"))
 DATA: Y=col(source(s), name("Y"))
 DATA: Id=col(source(s), name("Id"), unit.category())
 GUIDE: axis(dim(1), label("X"))
 GUIDE: axis(dim(2), label("Y"))
 ELEMENT: path(position(X*Y), split(Id), closed())
END GPL.

*For some reason link.sequence isnt working, but link hull is fine.
GGRAPH
  /GRAPHDATASET NAME="graphdataset" VARIABLES=X Y Id
  REPORTMISSING=NO
  /GRAPHSPEC SOURCE=INLINE.
BEGIN GPL
 SOURCE: s=userSource(id("graphdataset"))
 DATA: X=col(source(s), name("X"))
 DATA: Y=col(source(s), name("Y"))
 DATA: Id=col(source(s), name("Id"), unit.category())
 GUIDE: axis(dim(1), label("X"))
 GUIDE: axis(dim(2), label("Y"))
 ELEMENT: polygon(position(link.hull(X*Y)), split(Id), color.interior(color.grey), transparency.interior(transparency."0.7"))
END GPL.


