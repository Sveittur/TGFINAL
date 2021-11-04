from pygame import mixer
class soundBoard:
    def __init__(self):
        self.headshotSound = mixer.Sound("sounds/headshot.wav")

        self.akShootSound = mixer.Sound("sounds/akShootSound.wav")
        self.akDeploySound = mixer.Sound("sounds/akDeploySound.wav")

        self.pistolShootSound = mixer.Sound("sounds/pistolFireSound.wav")
        self.pistolDeploySound = mixer.Sound("sounds/pistolDeploySound.wav")
        
        self.knifeDeploySound = mixer.Sound("sounds/knifeDeploySound.wav")
        self.knifeWiffSound = mixer.Sound("sounds/knifeWiffSound.wav")
        self.knifeKillSound = mixer.Sound("sounds/knifeKillSound.wav")

    def playHeadshot(self):
        self.headshotSound.play()

    def playAkShoot(self):
        self.akShootSound.play()
    
    def playAkDeploy(self):
        self.akDeploySound.play()
    
    def stopAkDeploy(self):
        self.akDeploySound.stop()

    def playPistolShoot(self):
        self.pistolShootSound.play()
    
    def playPistolDeploy(self):
        self.pistolDeploySound.play()
    
    def stopPistolDeploy(self):
        self.pistolDeploySound.stop()

    def playKnifeDeploy(self):
        self.knifeDeploySound.play()
    
    def stopKnifeDeploy(self):
        self.knifeDeploySound.stop()

    def playKnifeWiff(self):
        self.knifeWiffSound.play()

    def stopKnifeWiff(self):
        self.knifeWiffSound.stop()
    
    def playKnifeKill(self):
        self.knifeKillSound.play()