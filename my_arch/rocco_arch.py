import sys
sys.path.append('./')
from pycore.tikzeng import *
from pycore.blocks import *

###################################################################################
# Funzione personalizzata per input con didascalia
###################################################################################
def to_input_labeled(pathfile, to='(-3,0,0)', width=8, height=8, name="input",
                     caption="(300×150×1)"):
    """
    Disegna un nodo con l'immagine e sotto una piccola didascalia
    che mostra, ad esempio, la dimensione '300×150×1'.
    """
    return r"""
\node[canvas is zy plane at x=0] (""" + name + """) at """+ to +""" {
    \includegraphics[width="""+ str(width)+"cm"+""",height="""+ str(height)+"""cm]{"""+ pathfile +"""}
};
\node[font=\scriptsize, align=center, text=black]
    (""" + name + """-caption)
    at (""" + name + """-south) [shift={(0, -1)}]
    { """ + caption + r""" };
"""

###################################################################################
# Funzione personalizzata per PoolShifted (se non l'hai già) 
###################################################################################
def to_PoolShifted(name, offset="(0,0,0)", to="(0,0,0)",
                   width=1, height=32, depth=32, opacity=0.5, caption=" "):
    return r"""
\pic[shift={ """ + offset + """ }] at """ + to + """
    {BoxMaxPool={
        name=""" + name + """,
        caption={""" + caption + r"""},
        fill=\PoolColor,
        opacity=""" + str(opacity) + """,
        height=""" + str(height) + """,
        width=""" + str(width) + """,
        depth=""" + str(depth) + """
        }
    };
"""

###################################################################################
# Architettura con le 3 modifiche
###################################################################################
arch = [ 
    to_head('.'), 
    to_cor(),
    to_begin(),
    
    # (1) Input immagine 300×150 con didascalia
    to_input_labeled(
        pathfile='./spec.jpeg',
        to='(-3,0,0)',
        width=12,
        height=6,
        name='input',
        caption=""
    ),
    
    # (2) Primo Blocco: Conv2D(32) + MaxPool
    to_ConvConvRelu(
        name='cr1',
        s_filer="295×148",
        n_filer=(32,32),
        offset="(0,0,0)", to="(0,0,0)",
        width=(3,3),
        height=20,  # invertito
        depth=40,   # invertito
        caption="{Conv2D (32, 6×3, ReLU)}"
    ),
    to_PoolShifted(
        name='p1',
        offset="(0,0,0)", to="(cr1-east)",
        width=1,
        height=15,
        depth=30,
        opacity=0.5,
        caption="{MaxPool2D 147×74}"
    ),
    
    # (3) Secondo Blocco: Conv2D(64) + MaxPool
    to_ConvConvRelu(
        name='cr2',
        s_filer="142×72",
        n_filer=(64,64),
        offset="(3.5,0,0)", to="(p1-east)",
        width=(4,4),
        height=12,
        depth=25,
        caption="{Conv2D (64, 6×3, ReLU)}"
    ),
    to_PoolShifted(
        name='p2',
        offset="(0,0,0)", to="(cr2-east)",
        width=1,
        height=9,
        depth=18,
        opacity=0.5,
        caption="{MaxPool2D 71×36}"
    ),
    
    # (4) Terzo Blocco: Conv2D(128) + MaxPool
    to_ConvConvRelu(
        name='cr3',
        s_filer="66×34",
        n_filer=(128,128),
        offset="(3.5,0,0)", to="(p2-east)",
        width=(5,5),
        height=8,
        depth=17,
        caption="{Conv2D (128, 6×3, ReLU)}"
    ),
    to_PoolShifted(
        name='p3',
        offset="(0,0,0)", to="(cr3-east)",
        width=1,
        height=6,
        depth=12,
        opacity=0.5,
        caption="{MaxPool2D 33×17}"
    ),
    
    # (5) Flatten => ADESSO 1×64×64, e piu' grande
    to_Conv(
        name='flatten',
        s_filer="1×64×64",  # <--- Cambiato da 71808 a 1×64×64
        n_filer=1,
        offset="(2,0,0)", to="(p3-east)",
        width=3,   # <--- Ingrandito
        height=7,  # <--- Ingrandito
        depth=7,   # <--- Ingrandito
        caption="{Flatten (1×64×64)}"
    ),
    
    # (6) Dense(128, ReLU) => Ingrandito
    to_Conv(
        name='dense1',
        s_filer=128,
        n_filer=128,
        offset="(2,0,0)", to="(flatten-east)",
        width=5,  # <--- Ingrandito
        height=10,
        depth=10,
        caption="{Dense (128, ReLU)}"
    ),
    
    # (7) Output: Dense(1, Sigmoid)
    to_Conv(
        name='output',
        s_filer=1,
        n_filer=1,
        offset="(2,0,0)", to="(dense1-east)",
        width=3,  # <--- un pochino più grande
        height=3,
        depth=3,
        caption="{Dense (1, Sigmoid)}"
    ),
    
    # Connessioni
    to_connection("p1", "cr2"),
    to_connection("p2", "cr3"),
    to_connection("p3", "flatten"),
    to_connection("flatten", "dense1"),
    to_connection("dense1", "output"),
    
    to_end()
]

def main():
    namefile = str(sys.argv[0]).split('.')[0]
    to_generate(arch, namefile + '.tex')

if __name__ == '__main__':
    main()