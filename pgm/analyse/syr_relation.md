

pré-scriptum : rien a faire dans analyser !


15 + 8 + 12 +18 + 27 = 80
L3 = 15,23,35,53,80

7 + 4 + 6 + 9 = 26
L2 = 7,11,17,26

3 + 2 + 3 = 8
L1 = 3,5,8

1 + 1 = 2 
L0 = 1,2



Ln[k] * 2+1 = Ln+1[k]

1*2+1 = 3, 3*2+1 = 7 ...
2*2+1 = 5, 5*2+1 = 11, 8*2+1=17 ...

Ln[k] * 3+2 = Ln+1[k+1]

1*3+2 = 5, 2*3+2 = 8
3*3+2 = 11,5*3+2=17,8*3+2=26 ...

Ln[0] = 2^n-1

e0,0 = 1
e1,0 = 2 ; e1,1=3
e2,0 = 4 ; e2,1 = 6; e2,2=9
...

en+1,0 = en *2
1,2,4,8...

en+1,n+1 =en,n *3 
1,3,9...

en+1,k = en,k-1 *3 = en,k *2
6 = 2*3 = 3*2 , 12 = 4*3 = 6*2

ENS : l'ensemble des ensemble majuscule ci dessous
ens : l'ensemble des ensemble minuscule ci dessous
omega = ens + ENS

{H : wH=(k,n,m) vH est H ssi vH = k*2^n*3^m-1} *k non multiple de 3 et 2 ,n et m sont N*
{h : wh=(k,n) vh est h ssi vh = k*2^n-1 } ou h est H avec m=0
{E : zE=(k,n,m) vE est E ssi vE = k*2^n*3^m}
{e : ze=(n,m) ve est E ssi ve = 2^n*3^m} ou e est E avec k=1
{F : uF=(k,n,m) vF est F ssi vF= k*4^n*3^n+1}
{f : uf=(n,m) vf est f ssi vf = 4^n*3^m+1} ou f est F avec k=1
{G : xG=(k,n,m) vG est G ssi vG = k*4^n*3^m} * k non multiple de 4 et 3,n et m sont N*
{g : ...} ou g est G avec k=1

"""
redondant !
{D : k*4^n*3^m}
{d : ...} ou d est D avec k=1
""" 
H et F sont les valeurs elle meme
alors que E,G sont les composant additifs qui permettent de se deplacer dans H et F

on note omega_d pour d=m+n l'ensemble au degres d 
et omega_d_t pour l'indice t au degres d defini dans l'interval [0,d] 


H inter G => avant derniere etape de croissance 