'''
File which handles the parsing of strings into syntax trees
'''
from syntax import *
from state import *
import re
from robot import Robot

def matchParen(s,i):
    l=s[i]
    if l=='(':
        r=")"
    elif l=="{":
        r="}"
    elif l=="[":
        r="]"
    elif l=="<":
        r=">"
    else: 
        raise Exception()
    cnt=0
    for j in range(i,len(s)):
        if s[j]==l:
            cnt+=1
        elif s[j]==r:
            cnt-=1
        if cnt==0:
            return j
    return None


def findTopLevel(s):
    '''
    Takes in a string and finds the top level syntax token along with arguments
    Returns: operator*string list
    '''
    ops_list = ['?', ':=', ';', '++']
    
    s = s.strip()
    # If {} surround the entire string, strip and recurse
    if(s[0] == '{' and matchParen(s, 0) == len(s) - 1):
        return findTopLevel(s[1:-1])

    # If {}* surround the entire string, return loop
    if(s[0] == '{' and matchParen(s, 0) == len(s) - 2 and s[-1] == "*"):
        return (Loop, [s[1:-2]])
    
    top_op = None
    top_op_idx = None
    i = 0
    while(i < len(s)):
        if(s[i] == '{'):
            # Skip to matching paren
            j = matchParen(s,i)
            if j is None:
                raise Exception('Unmatched left bracket in HP')
            i = j + 1
            continue
        elif (s[i] == "\'"):
            # Found ', entire string is ODE
            return(ODE, [s])
        elif (s[i] in ops_list):
            if top_op is None or ops_list.index(s[i]) > ops_list.index(top_op):
                # Replace if binds looser
                top_op = s[i]    
                top_op_idx = i 
            i = i + 1
        elif (s[i:i+2] in ops_list):
            if top_op is None or ops_list.index(s[i:i+2]) > ops_list.index(top_op):
                # Replace if binds looser
                top_op = s[i:i+2]
                top_op_idx = i
            i = i + 2
        else:
            i = i + 1
    
    if(top_op is None):
        return (None, s)
    
    op_class = None
    if(top_op == ':='):
        op_class = Assign
    elif (top_op == '++'):
        op_class = Choice
    elif (top_op == ';'):
        op_class = Compose
    elif (top_op == '?'):
        return (Test, [s[1:]])
    
    # Split up the string by top_op location
    return (op_class, [s[:top_op_idx], s[top_op_idx+len(top_op):]])

def isExp(s):
    '''
    Returns true if the string is a well-formed expression
    '''
    #checks that there are no =,<,>,!,++,{,}
    prohibited=["=","<",">","!","++","{","}",";","true","false"]
    for p in prohibited:
        if p in s:return False
    return True

def isQEForm(s):
    '''
    Returns true if the string is a formula with no further decomposition needed
    to determine truth value
    '''
    prohibited=["?",":=",";","++","}","{"]
    for p in prohibited:
        if p in s:return False
    return not isExp(s)

def parseHP(s):
    '''
    Takes a string representing a hybrid program and returns a syntax tree
    by recursively constructing it
    '''
    if isExp(s):
        return Term(s)
    if isQEForm(s):
        return Form(s)
    obj,args=findTopLevel(s)
    if obj==ODE:return ODE(args[0])
    argobjs=[parseHP(a) for a in args]
    return obj(*argobjs)

def sanitize(s):
    '''
    Replaces all the weird KX syntax with python syntax
    '''
    replaces = {"&":" and ","|":" or ","^":"**","!":"not "}
    for k in replaces:
        s=s.replace(k,replaces[k])
    return s

def firstInt(s):
  for i in range(len(s)):
    if s[i].isdigit():return i
  return -1
  
def parse(s):
    '''
    Takes in an entire Keymaera program and parses the variables, constants,
    program, and pre/post conditions
    returns: State * Form * Form * HP * robot list  
    (state, precons, postcons, HP syntax tree, list of Robot objects)
    '''
    #do some sanitation
    if s.find("!=")>=0:
      raise Exception("Can't have the symbol '!=' in the program")
    findend = lambda st,w: st.find(w)+len(w)#convenience
    s=sanitize(s)
    #0. remove comments
    s = re.sub(r'\/\*.+?\*\/','', s)
    #1. parse the variables out
    assert(s.find("ProgramVariables")>=0 or s.find("Definitions")>=0)
    defs=s[findend(s,'Definitions'):]
    defs=defs[:defs.find('End.')].strip()
    variables = s[findend(s,'ProgramVariables'):]
    variables = variables[:variables.find("End.")].strip()
    state=State()
    robot_dicts={}#maps from id->dict
    for line in defs.splitlines()+variables.splitlines():
        if 'Real' not in line:continue
        assignment = line[findend(line,'Real '):line.find(';')]
        if ":" in assignment:
          #parse out the type, and delete it to be unchanged for the following lines
          typeend=assignment.find("=") if "=" in assignment else len(assignment)
          typ = assignment[findend(assignment,":"):typeend].strip()
          #update the dicts 
          rob_id=int(typ[firstInt(typ):])
          var_name=typ[:firstInt(typ)]
          if rob_id not in robot_dicts:
            d=dict()
            robot_dicts[rob_id]=d
          else:
            d=robot_dicts[rob_id]
          d[var_name]=assignment[:assignment.find(":")]
          assignment=assignment[:assignment.find(":")]+assignment[typeend:]
        if '=' in assignment:
            val = float(assignment[findend(assignment,'='):].strip())
            state.addVar(assignment[:assignment.find('=')].strip(),val)
        else:
            state.addVar(assignment.strip())
    robot_list=[Robot(robot_dicts[k],k) for k in robot_dicts]
    #2. isolate the program section
    progsec = s[findend(s,'Problem'):]
    progsec = progsec[:progsec.find("End.")].strip()
    #3. find precon and postcon
    precon = progsec[findend(progsec,'('):matchParen(progsec,progsec.find("("))]
    progsec= progsec[findend(progsec,"->"):].strip()
    hpstring = progsec[1:matchParen(progsec,0)]
    # print("precon: ",precon)
    print("HP: ",hpstring)
    postcon=progsec[matchParen(progsec,0)+1:].strip()
    # print("postcon: ",postcon)
    # print("state:",state.vars())
    #4. parse HP inside box or diamond
    tree = parseHP(hpstring)
    return state,Form(precon),Form(postcon),tree,robot_list


if __name__=="__main__":
    testprog=\
'''
ArchiveEntry "testprog"
Definitions
    Real A = 2;
    Real kp;
    Real kd;
    Real T;
    
End.
ProgramVariables
    Real a;
    Real v;
    Real x;
    Real t;
    
    Real vThresh;
    Real xThresh;
End.
Problem
  ( kp > 0 & kd > 0        ) ->
  [{t:=0;{v' = kp * -1 * x, x'= v, t'=1 & t<T}}*]
  (v < vThresh & x < xThresh)
End.
End.
'''
    lab1=\
'''
ProgramVariables  
      Real pos;      
      Real vel;      
      Real acc;      
      Real station;  
    End.  
      
    Problem  
      (pos < station & vel > 0  )
    ->  
      [  
        acc := (-vel*vel)/(2*(station-pos));  
        {pos' = vel, vel' = acc & vel >= 0}  
      ](  
        (pos<=station & (pos=station -> vel=0))  
        & (!(pos<station&vel=0))  
      )  
    End.
'''
    lab1_3=\
    lab3=\
'''
Definitions
  Real A;    /* Robot's maximum acceleration*/
  Real B;    /* Robot's maximum braking */
End.

ProgramVariables
  Real x; /* Position of robot in x direction */
  Real y; /* Position of robot in y direction */

  Real dx; /* Unit vector in direction of travel, x direction */
  Real dy; /* Unit vector in direction of travel, y direction */

  Real trackr; /* Robot track radius */
  Real cx; /* center of track x*/
  Real cy; /* center of track y*/

  Real v; /* Linear velocity of robot */
  Real a; /* Linear acceleration of robot */
End.

Problem
  ((cx-x)^2+(cy-y)^2=trackr^2 & dx^2+dy^2=1)
  ->
  [
    {
      /* Control steering using trackr */
      {trackr:=*;?trackr!=0;cx:=x-dy*trackr;cy:=y+dx*trackr};
      /* Control acceleration (a) */
      {a:=*;?a>-B&a<A};
      {v'=a,x'=dx*v,y'=dy*v,dx'=-v*dy/trackr,dy'=v*dx/trackr /* differential equations for this system. Make sure everything that changes continuously is included. */
       & v >= 0
      }
    }*
  ]((cx-x)^2+(cy-y)^2=trackr^2) /* Safety condition. */
End.
End.
'''
    lab3=\
'''
Definitions  
  Real r;  /* Racetrack radius */  
  Real T;  /* Maximal time interval between consecutive triggerings of the controller */  
  Real A;  /* The robot accelerates with acceleration A */  
  Real B;  /* The robot brakes with acceleration -B */  
  
  Real ox; /* Cartesian coordinate x of the obstacle */  
  Real oy; /* Cartesian coordinate y of the obstacle */  
  
  /* Optional: function/predicate definitions, with explanatory comment. */  
  /*                                                                            
                                                                               */  
                                                                                
End.  
  
ProgramVariables  
  Real t;  /* Elapsed time since the last controller triggering */  
  Real x;  /* Cartesian coordinate x of the robot */  
  Real y;  /* Cartesian coordinate y of the robot */  
  Real v;  /* Linear velocity (ground speed) of the robot */  
  Real a;  /* Linear acceleration of the robot */  
End.  
  
Problem  
  (  
    /* Constant assumptions and initial conditions */  
    (T > 0 & A > 0 & B > 0 & r > 0 & ox = -r & oy = 0) & v >= 0 &  
    0.5*v^2/B < (x-ox)    
     & x^2 + y^2 = r^2   
      
  )  
  ->  
  [  
    {  
      /* Robot controller */  
      {  
        {  
          ?(  
            /* When is it safe to accelerate? */  
            y>=0 & 0.5*(v+A*T)^2/B + 0.5*A*T^2 + v*T < (x-ox)  
              
          );  
          a := A  
        } ++ { a := -B }  
      };  
      /* Continuous dynamic */  
      t:=0;  
      { x'=-v*y/r, y'=v*x/r, v'=a, t'=1 & v >= 0 & t <= T }  
    }*  
    
  ]  
  /* Safety condition: the robot stays on the track and never hits the obstacle */  
  (x^2+y^2=r^2 & !(x=ox & y=ox))  
End.
'''
    lab4_1=\
'''
Definitions
  Real A;    /* Robot's maximum acceleration*/
  Real B;    /* Robot's maximum braking */
End.

ProgramVariables
  Real x; /* Position of robot in x direction */
  Real y; /* Position of robot in y direction */

  Real dx; /* Unit vector in direction of travel, x direction */
  Real dy; /* Unit vector in direction of travel, y direction */

  Real trackr; /* Robot track radius */
  Real cx; /* center of track x*/
  Real cy; /* center of track y*/

  Real v; /* Linear velocity of robot */
  Real a; /* Linear acceleration of robot */
End.

Problem
  ((cx-x)^2+(cy-y)^2=trackr^2 & dx^2+dy^2=1)
  ->
  [
    {
      /* Control steering using trackr */
      {trackr:=*;?trackr!=0;cx:=x-dy*trackr;cy:=y+dx*trackr};
      /* Control acceleration (a) */
      {a:=*;?a>-B&a<A};
      {v'=a,x'=dx*v,y'=dy*v,dx'=-v*dy/trackr,dy'=v*dx/trackr /* differential equations for this system. Make sure everything that changes continuously is included. */
       & v >= 0
      }
    }*
  ]((cx-x)^2+(cy-y)^2=trackr^2) /* Safety condition. */
End.
End.
'''
    parsetest=\
'''
ProgramVariables
  Real x:x0 =  1; /* Position of robot in x direction */
  Real y:y0=1;
End.
Problem
(true)-> [{{x'=1 & x<.5};?x<10}++{x:=2}]x>1
End.
'''
    state,precon,postcon,tree,robots=parse(parsetest)
    # print(state.vars)
    # print(precon.arg)
    # print(postcon.arg)
    print("Tree:")
    tree.print()
    print("Traces:")
    traces=tree.expand(state)
    for choices,end_state in traces:
      print("Choices:",choices)
      print("End state",end_state.vars())
      print()

    s =Sim(parsetest)
