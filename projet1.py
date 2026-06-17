import random

class revenue :
    def __init__(self):
        self.revenue_annuel = int()

    def _beauté_chiffre_(self, element):
        try:
            nombre = float(element)
            return f"{nombre:,.2f}".replace(",", " ").replace(".", ",")
        except:
            return element   

    def revenue_net_annuel (self) :
        salaire = self.revenue_annuel
        impot = 0

        if salaire <= 11497:
            impot = 0

        elif salaire <= 26791:
            impot = (salaire - 11497) * 0.11

        elif salaire <= 74517:
            impot = (26791 - 11497) * 0.11
            impot += (salaire - 26791) * 0.30

        elif salaire <= 160336:
            impot = (26791 - 11497) * 0.11
            impot += (74517 - 26791) * 0.30
            impot += (salaire - 74517) * 0.41

        else:
            impot = (26791 - 11497) * 0.11
            impot += (74517 - 26791) * 0.30
            impot += (160336 - 74517) * 0.41
            impot += (salaire - 160336) * 0.45

        revenu_net = salaire - impot
        return round(revenu_net, 2)
    

            
    def revenue_net_mensuel(self) :
        salaire_mensuel = self.revenue_net_annuel() 
        salaire_mensuel_net = salaire_mensuel / 12 
        return round(salaire_mensuel_net,2)
    
    def __str__(self):
        return f"Votre revenu annuel brut {self._beauté_chiffre_(str(self.revenue_annuel))}€ correspond à {self._beauté_chiffre_(str(self.revenue_net_annuel()))}€/ans net et  {self._beauté_chiffre_(str(self.revenue_net_mensuel()))}€/mois net"




class SimulateurCrise:
    def __init__(self, revenu_annuel):
        self.revenu_annuel_crise = revenu_annuel

    def _beauté_chiffreS(self, element):
        try:
            nombre = float(element)
            return f"{nombre:,.2f}".replace(",", " ").replace(".", ",")
        except:
            return element
    

    def revenu_apres_crise(self):
        return float(self.revenu_annuel_crise) * 0.775


class pret_immobilier :
    def __init__(self) :
        self.credit = 0.0
        self.taux_pret = 0.0
        self.dure_en_annee = 0

    def _beauté_chiffre(self, element):
        try:
            nombre = float(element)
            return f"{nombre:,.2f}".replace(",", " ").replace(".", ",")
        except:
            return element



    def calcul_mensualite_pret(self) :
        if self.dure_en_annee <= 0 :
            return 0
        else :
            if self.taux_pret == 0 :
                Mensualite = self.credit / (self.dure_en_annee * 12)
            else :
                Mensualite = (self.credit*((self.taux_pret)/1200)) / (1 - ( 1 + (self.taux_pret) / 1200 ) **( - (self.dure_en_annee * 12)))
            return round(Mensualite, 2)
    
    def montant_total_à_rembourser(self) :
        nombre_de_mois = self.dure_en_annee * 12
        addition_sale = self.calcul_mensualite_pret()* nombre_de_mois
        return round(addition_sale, 2)
    
    def etendue_pret(self) :
        difference = self.montant_total_à_rembourser() - self.credit
        return round(difference, 2)

    def diff_pourecentage(self) :
        difference_pourcentage = (( self.montant_total_à_rembourser() - self.credit ) / ( self.credit )) * 100
        return round(difference_pourcentage, 2)

    def afficher(self) :
        print(f"La mensualité de votre prêt d'une valeur de {self.credit} € sur {self.dure_en_annee} ans à un taux de {self.taux_pret}% est de :",self.calcul_mensualite_pret()," €/mois")
        print("Vous aurez payé à la fin", self.montant_total_à_rembourser(),"€")
        print(f"Vous payerez ainsi {self.etendue_pret()} € d'intéret en plus des {self.credit} €, représentant {self.diff_pourecentage()} % de votre prêt")

        return f"""
        <p>
        La mensualité de votre prêt d'une valeur de {self._beauté_chiffre(str(self.credit))} € sur {self.dure_en_annee} ans à un taux de {self._beauté_chiffre(str(self.taux_pret))}% est de : {self._beauté_chiffre(str(self.calcul_mensualite_pret()))} €/mois
        </p>

        <p>
        Vous aurez payé à la fin {self._beauté_chiffre(str(self.montant_total_à_rembourser()))} €
        </p>

        <p>
        Vous payerez ainsi {self._beauté_chiffre(str(self.etendue_pret()))} € d'intérêt en plus des {self._beauté_chiffre(str(self.credit))} €, représentant {self._beauté_chiffre(str(self.diff_pourecentage()))} % de votre prêt
        </p>
        """

    
    def mensualite_interet_et_pret(self) :
        duree = (self.dure_en_annee) * 12
        capital_restant = self.credit
        texte = ""
        for i in range(1 , duree + 1) :
            if i != duree :
                rembourse_I = capital_restant * ((self.taux_pret) / 1200) 
                rembourse_c = self.calcul_mensualite_pret() - rembourse_I
                capital_restant = capital_restant - rembourse_c  
                print(f"Mois n°{i} : Vous rembourser {self._beauté_chiffre(str(rembourse_I))} € d'intéret, {self._beauté_chiffre(str(rembourse_c))} € de prêt et il vous reste {self._beauté_chiffre(str(capital_restant))} € à rembourser.")
                texte += f"""
                <p>
                Mois n°{i} : Vous remboursez {self._beauté_chiffre(str(rembourse_I))} € d'intérêt,
                {self._beauté_chiffre(str(rembourse_c))} € de capital,
                reste {self._beauté_chiffre(str(capital_restant))} €
                </p>
                """
            else :
                capital_restant = 0.00
                print(f"Mois n°{i} : Vous rembourser {self._beauté_chiffre(str(rembourse_I))} € d'intéret, {self._beauté_chiffre(str(rembourse_c))} € de prêt et il vous reste {self._beauté_chiffre(str(capital_restant))} € à rembourser.")
                texte += f"""
                <p>
                Mois n°{i} : Vous remboursez {self._beauté_chiffre(str(rembourse_I))} € d'intérêt,
                {self._beauté_chiffre(str(rembourse_c))} € de capital,
                reste {self._beauté_chiffre(str(capital_restant))} €
                </p>
                """
        return texte


    def compare(self,autre) :
        if self.credit == autre.credit :
            total_self = self.montant_total_à_rembourser()
            total_autre = autre.montant_total_à_rembourser()

            if total_self < total_autre :
                print("")
                print(f"Le prêt le plus intéressant est : {self._beauté_chiffre(str(self.credit))} € à un taux de {self._beauté_chiffre(str(self.taux_pret))}% sur {self.dure_en_annee} ans.")
                return f"""
                <p>
                Le prêt le plus intéressant est : {self._beauté_chiffre(str(self.credit))} € à un taux de {self._beauté_chiffre(str(self.taux_pret))}% sur {self.dure_en_annee} ans.
                </p>
                """
                
            elif total_self > total_autre :
                print("")
                print(f"Le prêt le plus intéressant est : {self._beauté_chiffre(str(autre.credit))} € à un taux de {self._beauté_chiffre(str(autre.taux_pret))}% sur {autre.dure_en_annee} ans.")
                return f"""
                <p>
                Le prêt le plus intéressant est : {self._beauté_chiffre(str(autre.credit))} € à un taux de {self._beauté_chiffre(str(autre.taux_pret))}% sur {autre.dure_en_annee} ans.
                </p>
                """
            else :
                print("")
                print("Les deux prêt sont équivalents")
                return f"""
                <p>
                Les deux prêt sont équivalents.
                </p>
                """

        else :
            print("")
            print(" Nous ne pouvons pas déterminer lequel est le mieux car ce n'est pas la même somme d'emprunt")
            return f"""
            <p>
            Nous ne pouvons pas déterminer lequel est le mieux car ce n'est pas la même somme d'emprunt.
            </p>
            """

    def capacite_emprunt (self,  salaire_mensuel_net) :
        rembourse_pret =  self.calcul_mensualite_pret()
        salaire_compare = 0.35*salaire_mensuel_net
        if rembourse_pret > salaire_compare  :
            print(f"Nous vous déconseillons de prendre le prêt de {self._beauté_chiffre(str(self.credit))}€ au vu de vos revenus car il faut rembourser {self._beauté_chiffre(str(rembourse_pret))}€/mois et 35% de votre salaire correspond à {self._beauté_chiffre(str(salaire_compare))}€/mois.")
            texte = f"""
            <p>
            Nous vous déconseillons de prendre le prêt de {self._beauté_chiffre(str(self.credit))}€ au vu de vos revenus car il faut rembourser {self._beauté_chiffre(str(rembourse_pret))}€/mois et 35% de votre salaire correspond à {self._beauté_chiffre(str(salaire_compare))}€/mois.
            </p>
            """
            
        else :
            print(f"Vous êtes en mesure de faire le prêt de {self._beauté_chiffre(str(self.credit))}€ car il faut rembourser {self._beauté_chiffre(str(rembourse_pret))}€/mois et 35% de votre salaire correspond à {self._beauté_chiffre(str(salaire_compare))}€/mois..")
            texte = f"""
            <p>
            Vous êtes en mesure de faire le prêt de {self._beauté_chiffre(str(self.credit))}€ car il faut rembourser {self._beauté_chiffre(str(rembourse_pret))}€/mois et 35% de votre salaire correspond à {self._beauté_chiffre(str(salaire_compare))}€/mois.
            </p>
            """
        return texte
    
    def tableau_html(self):
        duree = self.dure_en_annee * 12
        capital_restant = self.credit
        texte = ""

        for i in range(1, duree + 1):
            interet = capital_restant * (self.taux_pret / 1200)
            capital = self.calcul_mensualite_pret() - interet
            capital_restant -= capital

            if i == duree:
                capital_restant = 0

            texte += f"""
            <tr>
                <td>{i}</td>
                <td>{self._beauté_chiffre(str(round(interet,2)))}</td>
                <td>{self._beauté_chiffre(str(round(capital,2)))}</td>
                <td>{self._beauté_chiffre(str(round(capital_restant,2)))}</td>
            </tr>
            """

        return texte
    
# print("Vous voulez avoir des infos sur votre prêt, tapez 1")
# print("Vous voulez comparez deux prêts, tapez 2")
# choix = int(input("saisissez votre choix :"))

 

def main():
    print("1 - Info revenu + prêt")
    print("2 - Comparer prêts")

    choix = int(input("Choix : "))

    if choix == 1:
        print("\n--- REVENUE ---")
        r = revenue()
        r.revenue_annuel = int(input("Salaire brut : "))
        print(f"\n{r}")

        print("\n--- PRET ---")
        pret = pret_immobilier()
        pret.credit = float(input("Crédit : "))
        pret.taux_pret = float(input("Taux : "))
        pret.dure_en_annee = int(input("Durée : "))
        pret.mensualite_interet_et_pret()

        print("\n===== RESULTATS =====")
        pret.afficher()

        print("\n===== CONSEILLE =====")
        pret.capacite_emprunt(r.revenue_net_mensuel())

    elif choix == 2:
        print("\n--- REVENUE ---")
        r = revenue()
        r.revenue_annuel = int(input("Salaire brut : "))
        print(f"\n{r}")

        print("\n--- PRET 1 ---")
        pret1 = pret_immobilier()
        pret1.credit = float(input("Crédit 1 : "))
        pret1.taux_pret = float(input("Taux 1 : "))
        pret1.dure_en_annee = int(input("Durée 1 : "))
        pret1.mensualite_interet_et_pret()

        print("\n--- PRET 2 ---")
        pret2 = pret_immobilier()
        pret2.credit = float(input("Crédit 2 : "))
        pret2.taux_pret = float(input("Taux 2 : "))
        pret2.dure_en_annee = int(input("Durée 2 : "))
        pret2.mensualite_interet_et_pret()  

        print("\n===== PRET 1 =====")
        pret1.afficher()
        pret1.capacite_emprunt(r.revenue_net_mensuel())

        print("\n===== PRET 2 =====")
        pret2.afficher()
        pret2.capacite_emprunt(r.revenue_net_mensuel())

        print("\n===== COMPARAISON =====")
        pret1.compare(pret2)
if __name__ == "__main__":   
    main()

