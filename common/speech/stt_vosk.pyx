#!python
#cython: language_level=3

FRAME_MAX_VALUE = 2 ** 15 - 1
NORMALIZE_MINUS_ONE_dB = 10 ** (-1.0 / 20)
FACTOR=float(NORMALIZE_MINUS_ONE_dB * FRAME_MAX_VALUE)
last_normalize_factor=1

def normalize(signed short[:] contents):
    global last_normalize_factor

    maximum=0
    for i in range(contents.shape[0]):
        val=abs(contents[i])
        if val>maximum:
            maximum=val

    normalize_factor = (FACTOR / maximum)

    #for to be more smooth if we became too not loud
    if normalize_factor > last_normalize_factor :
        normalize_factor = (normalize_factor+last_normalize_factor)/2
    last_normalize_factor = normalize_factor

    print (f"normalize_factor={normalize_factor}")

    for i in range(contents.shape[0]):
        val=int(contents[i] * normalize_factor)
        contents[i]=val

def clear(signed short[:] contents):
    for i in range(contents.shape[0]):
        contents[i]=0
