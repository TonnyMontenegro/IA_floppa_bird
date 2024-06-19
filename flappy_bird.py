import os
import pygame
import neat
import random

pygame.font.init()  # inicializar la fuente

ANCHO_DE_VENTANA = 600 # Ancho de la ventana
ALTO_DE_VENTANA = 800 # Altura de la ventana
SUELO = 730 # Altura del suelo
FUENTE_ESTADISTICAS = pygame.font.SysFont("comicsans", 50) # Fuente para las estadísticas (comic sans para mas placer)
FUENTE_FINAL = pygame.font.SysFont("comicsans", 70)
DIBUJAR_LINEAS = False

VENTANA = pygame.display.set_mode((ANCHO_DE_VENTANA, ALTO_DE_VENTANA))
pygame.display.set_caption("Flappy Bird IA HD PRO MAX")

imagen_tubo = pygame.transform.scale2x(pygame.image.load(os.path.join("imagenes","tuberia.png")).convert_alpha())
imagen_fondo = pygame.transform.scale(pygame.image.load(os.path.join("imagenes","fondo.png")).convert_alpha(), (600, 900))
imagenes_pajaro = [pygame.transform.scale2x(pygame.image.load(os.path.join("imagenes","pajaro" + str(x) + ".png"))) for x in range(1,4)]
imagen_base = pygame.transform.scale2x(pygame.image.load(os.path.join("imagenes","suelo.png")).convert_alpha())

gen = 0

class Pajaro:
    """
    Clase que representa al pájaro del juego
    """
    ROTACION_MAXIMA = 25
    IMAGENES = imagenes_pajaro
    VELOCIDAD_ROTACION = 20
    TIEMPO_ANIMACION = 5

    def __init__(self, x, y):
        """
        Inicializa el objeto del pajaro
        :param x: posición inicial x (int)
        :param y: posición inicial y (int)
        :return: None
        """
        self.x = x
        self.y = y
        self.inclinacion = 0  # grados de inclinación
        self.contador_tiempo = 0
        self.velocidad = 0
        self.altura = self.y
        self.contador_imagen = 0
        self.imagen = self.IMAGENES[0]

    def saltar(self):
        """
        Hace que el pájaro salte
        :return: None
        """
        self.velocidad = -10.5
        self.contador_tiempo = 0
        self.altura = self.y

    def mover(self):
        """
        Hace que el pájaro se mueva
        :return: None
        """
        self.contador_tiempo += 1

        # para la aceleración hacia abajo
        desplazamiento = self.velocidad*(self.contador_tiempo) + 0.5*(3)*(self.contador_tiempo)**2  # calcular desplazamiento

        # velocidad terminal
        if desplazamiento >= 16:
            desplazamiento = (desplazamiento/abs(desplazamiento)) * 16

        if desplazamiento < 0:
            desplazamiento -= 2

        self.y = self.y + desplazamiento

        if desplazamiento < 0 or self.y < self.altura + 50:  # inclinación hacia arriba
            if self.inclinacion < self.ROTACION_MAXIMA:
                self.inclinacion = self.ROTACION_MAXIMA
        else:  # inclinación hacia abajo
            if self.inclinacion > -90:
                self.inclinacion -= self.VELOCIDAD_ROTACION

    def dibujar(self, ventana):
        """
        Dibuja al pájaro
        :param ventana: ventana o superficie de pygame
        :return: None
        """
        self.contador_imagen += 1

        # Para la animación del pájaro, se recorren tres imágenes
        if self.contador_imagen <= self.TIEMPO_ANIMACION:
            self.imagen = self.IMAGENES[0]
        elif self.contador_imagen <= self.TIEMPO_ANIMACION*2:
            self.imagen = self.IMAGENES[1]
        elif self.contador_imagen <= self.TIEMPO_ANIMACION*3:
            self.imagen = self.IMAGENES[2]
        elif self.contador_imagen <= self.TIEMPO_ANIMACION*4:
            self.imagen = self.IMAGENES[1]
        elif self.contador_imagen == self.TIEMPO_ANIMACION*4 + 1:
            self.imagen = self.IMAGENES[0]
            self.contador_imagen = 0

        # para que el pájaro no aletee cuando está en picada
        if self.inclinacion <= -80:
            self.imagen = self.IMAGENES[1]
            self.contador_imagen = self.TIEMPO_ANIMACION*2


        # inclinar el pájaro
        rotar_imagen(ventana, self.imagen, (self.x, self.y), self.inclinacion)

    def obtener_mascara(self):
        """
        Obtiene la máscara para la imagen actual del pájaro
        :return: None
        """
        return pygame.mask.from_surface(self.imagen)


class Tuberia():
    """
    Representa un objeto de tuberia
    """
    ESPACIO = 200
    VELOCIDAD = 5

    def __init__(self, x):
        """
        Inicializa el objeto tuberia
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.altura = 0

        # donde está la parte superior e inferior del tuberia
        self.superior = 0
        self.inferior = 0

        self.TUBO_SUPERIOR = pygame.transform.flip(imagen_tubo, False, True)
        self.TUBO_INFERIOR = imagen_tubo

        self.pasado = False

        self.establecer_altura()

    def establecer_altura(self):
        """
        Establece la altura del tuberia, desde la parte superior de la pantalla
        :return: None
        """
        self.altura = random.randrange(50, 450)
        self.superior = self.altura - self.TUBO_SUPERIOR.get_height()
        self.inferior = self.altura + self.ESPACIO

    def mover(self):
        """
        Mueve el tuberia según la velocidad
        :return: None
        """
        self.x -= self.VELOCIDAD

    def dibujar(self, ventana):
        """
        Dibuja tanto la parte superior como la inferior del tuberia
        :param ventana: ventana o superficie de pygame
        :return: None
        """
        # dibujar parte superior
        ventana.blit(self.TUBO_SUPERIOR, (self.x, self.superior))
        # dibujar parte inferior
        ventana.blit(self.TUBO_INFERIOR, (self.x, self.inferior))


    def colisionar(self, pajaro, ventana):
        """
        Devuelve si un punto está colisionando con el tuberia
        :param pajaro: objeto Pajaro
        :return: Bool
        """
        mascara_pajaro = pajaro.obtener_mascara()
        mascara_superior = pygame.mask.from_surface(self.TUBO_SUPERIOR)
        mascara_inferior = pygame.mask.from_surface(self.TUBO_INFERIOR)
        desplazamiento_superior = (self.x - pajaro.x, self.superior - round(pajaro.y))
        desplazamiento_inferior = (self.x - pajaro.x, self.inferior - round(pajaro.y))

        punto_inferior = mascara_pajaro.overlap(mascara_inferior, desplazamiento_inferior)
        punto_superior = mascara_pajaro.overlap(mascara_superior,desplazamiento_superior)

        if punto_inferior or punto_superior:
            return True

        return False

class Suelo:
    """
    Representa el suelo móvil del juego
    """
    VELOCIDAD = 5
    ANCHO = imagen_base.get_width()
    IMAGEN = imagen_base

    def __init__(self, y):
        """
        Inicializa el objeto
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.ANCHO

    def mover(self):
        """
        Mueve el suelo para que parezca que se desplaza
        :return: None
        """
        self.x1 -= self.VELOCIDAD
        self.x2 -= self.VELOCIDAD
        if self.x1 + self.ANCHO < 0:
            self.x1 = self.x2 + self.ANCHO

        if self.x2 + self.ANCHO < 0:
            self.x2 = self.x1 + self.ANCHO

    def dibujar(self, ventana):
        """
        Dibuja el suelo. Son dos imágenes que se mueven juntas.
        :param ventana: la superficie/ventana de pygame
        :return: None
        """
        ventana.blit(self.IMAGEN, (self.x1, self.y))
        ventana.blit(self.IMAGEN, (self.x2, self.y))


def rotar_imagen(surf, imagen, esquina_superior_izquierda, angulo):
    """
    Rota una superficie y la dibuja en la ventana
    :param surf: la superficie en la que dibujar
    :param imagen: la superficie de imagen a rotar
    :param esquina_superior_izquierda: la posición superior izquierda de la imagen
    :param angulo: un valor flotante para el ángulo
    :return: None
    """
    imagen_rotada = pygame.transform.rotate(imagen, angulo)
    nuevo_rectangulo = imagen_rotada.get_rect(center = imagen.get_rect(topleft = esquina_superior_izquierda).center)

    surf.blit(imagen_rotada, nuevo_rectangulo.topleft)

def dibujar_ventana(ventana, pajaros, tubos, suelo, puntuacion, gen, indice_tubo):
    """
    Dibuja la ventana para el bucle principal del juego
    :param ventana: superficie/ventana de pygame
    :param pajaros: lista de pájaros
    :param tubos: lista de tubos
    :param puntuacion: puntuación del juego (int)
    :param gen: generación actual
    :param indice_tubo: índice del tuberia más cercano
    :return: None
    """
    if gen == 0:
        gen = 1
    ventana.blit(imagen_fondo, (0,0))

    for tuberia in tubos:
        tuberia.dibujar(ventana)

    suelo.dibujar(ventana)
    for pajaro in pajaros:
        # dibujar líneas desde el pájaro hasta el tuberia
        if DIBUJAR_LINEAS:
            try:
                pygame.draw.line(ventana, (255,0,0), (pajaro.x+pajaro.imagen.get_width()/2, pajaro.y + pajaro.imagen.get_height()/2), (tubos[indice_tubo].x + tubos[indice_tubo].TUBO_SUPERIOR.get_width()/2, tubos[indice_tubo].altura), 5)
                pygame.draw.line(ventana, (255,0,0), (pajaro.x+pajaro.imagen.get_width()/2, pajaro.y + pajaro.imagen.get_height()/2), (tubos[indice_tubo].x + tubos[indice_tubo].TUBO_INFERIOR.get_width()/2, tubos[indice_tubo].inferior), 5)
            except:
                pass
        # dibujar pájaro
        pajaro.dibujar(ventana)

    # puntuación
    etiqueta_puntuacion = FUENTE_ESTADISTICAS.render("Puntos: " + str(puntuacion),1,(255,255,255))
    ventana.blit(etiqueta_puntuacion, (ANCHO_DE_VENTANA - etiqueta_puntuacion.get_width() - 15, 10))

    # generaciones
    etiqueta_puntuacion = FUENTE_ESTADISTICAS.render("Gen: " + str(gen-1),1,(255,255,255))
    ventana.blit(etiqueta_puntuacion, (10, 10))

    # vivos
    etiqueta_puntuacion = FUENTE_ESTADISTICAS.render("Vivos: " + str(len(pajaros)),1,(255,255,255))
    ventana.blit(etiqueta_puntuacion, (10, 50))

    pygame.display.update()


def evaluar_genomas(genomas, config):
    """
    Ejecuta la simulación de la población actual de
    pájaros y establece su fitness en función de la distancia que
    alcanzan en el juego.
    """
    global VENTANA, gen
    ventana = VENTANA
    gen += 1

    # empezar creando listas que contengan el genoma en sí, la
    # red neuronal asociada al genoma y el
    # objeto pájaro que utiliza esa red para jugar
    redes = []
    pajaros = []
    fitnesses = []
    for id_genoma, genoma in genomas:
        genoma.fitness = 0  # empezar con un fitness de 0
        red = neat.nn.FeedForwardNetwork.create(genoma, config)
        redes.append(red)
        pajaros.append(Pajaro(230,350))
        fitnesses.append(genoma)

    suelo = Suelo(SUELO)
    tubos = [Tuberia(700)]
    puntuacion = 0

    reloj = pygame.time.Clock()

    ejecutar = True
    while ejecutar and len(pajaros) > 0:
        reloj.tick(30)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutar = False
                pygame.quit()
                quit()
                break

        indice_tubo = 0
        if len(pajaros) > 0:
            if len(tubos) > 1 and pajaros[0].x > tubos[0].x + tubos[0].TUBO_SUPERIOR.get_width():  # determinar si usar el primer o segundo
                indice_tubo = 1                                                                 # tuberia en la pantalla para la entrada de la red neuronal

        for x, pajaro in enumerate(pajaros):  # dar a cada pájaro una fitness de 0.1 por cada fotograma que se mantenga vivo
            fitnesses[x].fitness += 0.1
            pajaro.mover()

            # enviar la ubicación del pájaro, la ubicación del tuberia superior y la ubicación del tuberia inferior a la red y determinar si debe saltar o no
            salida = redes[pajaros.index(pajaro)].activate((pajaro.y, abs(pajaro.y - tubos[indice_tubo].altura), abs(pajaro.y - tubos[indice_tubo].inferior)))

            if salida[0] > 0.5:  # se utiliza una función de activación tangente hiperbólica, por lo que el resultado estará entre -1 y 1. si es mayor que 0.5, saltar
                pajaro.saltar()

        suelo.mover()

        tubos_a_eliminar = []
        agregar_tubo = False
        for tuberia in tubos:
            tuberia.mover()
            # comprobar colisión
            for pajaro in pajaros:
                if tuberia.colisionar(pajaro, ventana):
                    fitnesses[pajaros.index(pajaro)].fitness -= 1
                    redes.pop(pajaros.index(pajaro))
                    fitnesses.pop(pajaros.index(pajaro))
                    pajaros.pop(pajaros.index(pajaro))

            if tuberia.x + tuberia.TUBO_SUPERIOR.get_width() < 0:
                tubos_a_eliminar.append(tuberia)

            if not tuberia.pasado and tuberia.x < pajaro.x:
                tuberia.pasado = True
                agregar_tubo = True

        if agregar_tubo:
            puntuacion += 1
            # se puede añadir esta línea para dar más recompensa por pasar por un tuberia (no es necesario)
            for fitness in fitnesses:
                fitness.fitness += 5
            tubos.append(Tuberia(ANCHO_DE_VENTANA))

        for tubo_a_eliminar in tubos_a_eliminar:
            tubos.remove(tubo_a_eliminar)

        for pajaro in pajaros:
            if pajaro.y + pajaro.imagen.get_height() - 10 >= SUELO or pajaro.y < -50:
                redes.pop(pajaros.index(pajaro))
                fitnesses.pop(pajaros.index(pajaro))
                pajaros.pop(pajaros.index(pajaro))

        dibujar_ventana(VENTANA, pajaros, tubos, suelo, puntuacion, gen, indice_tubo)

        # break si la puntuación es mayor que 25 (solo para acelerar el proceso)
        if puntuacion > 50: 
            break


def run(archivo_config):
    """
    Ejecuta el algoritmo NEAT para entrenar una red neuronal para jugar a Flappy Bird.
    :param archivo_config: ubicación del archivo de configuración
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         archivo_config)

    # Crea la población, que es el objeto de nivel superior para una ejecución de NEAT.
    p = neat.Population(config)

    # Añade un informe de salida estándar para mostrar el progreso en la terminal.
    p.add_reporter(neat.StdOutReporter(True))
    estadisticas = neat.StatisticsReporter()

    # Ejecuta hasta 50 generaciones como maximo.
    ganador = p.run(evaluar_genomas, 50)

    # muestra las estadísticas finales
    p.add_reporter(estadisticas)


    # show final stats
    print('\Mejor gen:\n{!s}'.format(ganador))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
