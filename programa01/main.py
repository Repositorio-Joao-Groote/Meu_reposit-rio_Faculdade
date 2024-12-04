from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout


class RestauranteApp(App):
    def build(self):
        self.mesas = {}  
        self.labels_quantidade = {}  
        self.preco_pratos = {
            "Hambúrguer": 19.90, 
            "Pizza": 29.90, 
            "Refrigerante": 4.90, 
            "Sopa": 12.90,
            "Salada": 9.90,
            "Frango Grelhado": 24.90
        }  

        # Layout principal
        self.root = BoxLayout(orientation="horizontal")

        # Container das as mesas
        self.container_mesas = ScrollView(size_hint=(1, 1))
        self.mesas_layout = GridLayout(cols=3, spacing=10, size_hint_y=None)
        self.mesas_layout.bind(minimum_height=self.mesas_layout.setter("height"))
        self.container_mesas.add_widget(self.mesas_layout)

        # Layout dos botões do menu principal (lateral direita)
        self.botao_layout = BoxLayout(orientation='vertical', size_hint=(None, None), padding=[20, 20], spacing=10)
        self.botao_layout.width = 200  

        # Botão para adicionar mesas
        self.botao_adicionar = Button(
            text="Adicionar Mesa",
            size_hint=(None, None),
            size=(180, 55),  # Botão um pouco menor
        )
        self.botao_adicionar.bind(on_release=self.adicionar_mesa)

        # Botão para finalizar o pedido
        self.botao_fechar = Button(
            text="Finalizar",
            size_hint=(None, None),
            size=(180, 55),  
        )
        self.botao_fechar.bind(on_release=self.fechar_programa)

        self.botao_layout.add_widget(self.botao_adicionar)
        self.botao_layout.add_widget(self.botao_fechar)

        # Adiciona o layout dos botões no root
        self.root.add_widget(self.container_mesas)
        self.root.add_widget(self.botao_layout)

        return self.root

    def adicionar_mesa(self, instance):
        # Numeração das mesas
        num_mesa = max(self.mesas.keys(), default=0) + 1
        self.mesas[num_mesa] = {"pratos": {prato: 0 for prato in self.preco_pratos}, "total": 0.0}

        # Cria a mesa em si
        botao_mesa = Button(
            text=f"Mesa {num_mesa}",
            size_hint=(None, None),
            size=(180, 55),  
        )
        botao_mesa.bind(on_release=lambda x: self.abrir_mesa(num_mesa))
        self.mesas_layout.add_widget(botao_mesa)

    def abrir_mesa(self, num_mesa):
        popup_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Espaçamento
        spacer = BoxLayout(size_hint=(None, None), size=(1, 20))  
        popup_layout.add_widget(spacer)

        # ScrollView 
        scroll_pratos = ScrollView(size_hint=(1, None), size=(400, 400))
        box_pratos = BoxLayout(orientation="vertical", size_hint_y=None, spacing=20) 
        box_pratos.bind(minimum_height=box_pratos.setter("height"))

        for prato in self.mesas[num_mesa]["pratos"]:
            box_prato = BoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=10, padding=[0, 10])  
            label_prato = Label(text=prato, size_hint=(None, None), width=150)
            label_quantidade = Label(text="0", size_hint=(None, None), width=50)
            self.labels_quantidade[prato] = label_quantidade

            # + e - sempre bugados
            box_botoes = BoxLayout(orientation="horizontal", size_hint=(None, None), width=140, spacing=10, padding=[20, 0])  
            botao_menos = Button(text="-", size_hint=(None, None), size=(40, 40))
            botao_menos.bind(
                on_release=lambda x, p=prato, pr=prato: self.ajustar_prato(num_mesa, p, -1)
            )

            botao_mais = Button(text="+", size_hint=(None, None), size=(40, 40))
            botao_mais.bind(
                on_release=lambda x, p=prato, pr=prato: self.ajustar_prato(num_mesa, p, 1)
            )

            # tentativa de ajuste 04
            box_botoes.add_widget(botao_menos)
            box_botoes.add_widget(label_quantidade)
            box_botoes.add_widget(botao_mais)

            # tentativa de ajuste 04
            box_prato.add_widget(label_prato)
            box_prato.add_widget(box_botoes)

            box_pratos.add_widget(box_prato)

        scroll_pratos.add_widget(box_pratos)
        popup_layout.add_widget(scroll_pratos)

        # Valor a pagar
        self.label_total = Label(text=f"Total: R$ {self.mesas[num_mesa]['total']:.2f}")
        popup_layout.add_widget(self.label_total)

        # Finalizar
        botao_finalizar = Button(text="Finalizar", size_hint=(None, None), size=(180, 55))
        botao_finalizar.bind(on_release=lambda x: self.finalizar_pedido(num_mesa))
        popup_layout.add_widget(botao_finalizar)

        # Popup
        self.popup_mesa = Popup(
            title=f"Mesa {num_mesa}",
            content=popup_layout,
            size_hint=(None, None),
            size=(400, 600),
            auto_dismiss=True,
        )
        self.popup_mesa.open()

    def ajustar_prato(self, num_mesa, prato, ajuste):
        if prato not in self.mesas[num_mesa]["pratos"]:
            self.mesas[num_mesa]["pratos"][prato] = 0

        # tentativa de correção, bugs de preços
        nova_quantidade = self.mesas[num_mesa]["pratos"][prato] + ajuste
        if nova_quantidade < 0:
            nova_quantidade = 0
        self.mesas[num_mesa]["pratos"][prato] = nova_quantidade

        # Atualiza a label de quantidade
        self.labels_quantidade[prato].text = str(nova_quantidade)

        # Atualizar o total
        self.atualizar_total(num_mesa)

    def atualizar_total(self, num_mesa):
        total = 0.0
        for prato, quantidade in self.mesas[num_mesa]["pratos"].items():
            preco = self.preco_pratos[prato]
            total += quantidade * preco
        self.mesas[num_mesa]["total"] = total
        self.label_total.text = f"Total: R$ {self.mesas[num_mesa]['total']:.2f}"

    def finalizar_pedido(self, num_mesa):
        def confirmar(instance):
            # Remove a mesa
            del self.mesas[num_mesa]
            self.popup_mesa.dismiss()

            # Remove o botão da mesa
            for widget in self.mesas_layout.children[:]:
                if widget.text == f"Mesa {num_mesa}":
                    self.mesas_layout.remove_widget(widget)
                    break

        # Popup de confirmação
        popup_layout = BoxLayout(orientation="vertical", spacing=10)
        label_confirmar = Label(text="O pagamento foi efetuado?")
        botao_sim = Button(text="Sim", size_hint=(None, None), size=(100, 40))
        botao_nao = Button(text="Não", size_hint=(None, None), size=(100, 40))
        popup_layout.add_widget(label_confirmar)
        popup_layout.add_widget(botao_sim)
        popup_layout.add_widget(botao_nao)

        popup_confirmar = Popup(
            title="Confirmar",
            content=popup_layout,
            size_hint=(None, None),
            size=(300, 200),
            auto_dismiss=True,
        )
        botao_sim.bind(on_release=lambda x: (confirmar(x), popup_confirmar.dismiss()))
        botao_nao.bind(on_release=popup_confirmar.dismiss)

        popup_confirmar.open()

    def fechar_programa(self, instance):
        self.stop()


if __name__ == "__main__":
    RestauranteApp().run()
