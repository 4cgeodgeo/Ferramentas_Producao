## Ferramentas de Produção v3.4.14.2

* Corrigido bug de download de insumos que não sejam via protocolo smb - alterado para abrir URL no navegador.
* Adicioando possiblidade de carregamento de insumos WFS e WMS

## Ferramentas de Produção v3.4.14

Cliente QGIS 3 para uso do [Sistema de Apoio a Produção (SAP)](https://github.com/1cgeo/sap)

### Modificações da versão 3.4.14

* Melhorias no menu de classificação: Possibilidade de reordenar os botões já criados ou criar botões na posição desejada. Filtro textual e ordenamento do nome das camadas na criação de botão.

* Integrado o processing de _Estatísticas de Regras_ do DSGTools 4 com o Ferramentas de Produção. Quando a atividade conter regras o Ferramentas de Produção disponibiliza a rotina estatística de regras.

* Modificado o menu de classificação para não carregar camadas automaticamente no modo remoto, avisando o usuário caso a camada necessária não esteja carregada.

* Aba _controle_ é a aba principal no modo remoto.

* Adicionada ferramenta que liga e desliga a camada atual (com atalho Y).

* Adicionada ferramenta que liga e desliga a configuração _Mostrar marcadores apenas nas feições selecionadas_ (com atalho B).

* Adicionado atalho a ferramenta de ligar e desligar todos os labels do DSGTools 4 (atalho L).

* Adicionado botão que exibe os atalhos configurados pelo Ferramentas de Produção. Os seguintes atalhos estão configurados nessa versão:
    * Mesclar feições selecionadas : M
    * Corta Feições : C
    * Identificar feições : I
    * Adicionar feições : A
    * Desfazer seleção em todas as camadas : D
    * Ferramenta Vértice (Todas as Camadas) : N
    * Salvar para todas as camadas : Ctrl+S
    * Habilitar traçar : T
    * Remodelar feições : R
    * Medir área : Z
    * Medir linha : X
    * Seletor Genérico : S
    * Ferramenta de aquisição com ângulos retos : E
    * Edição topológica : H
    * Selecionar feições : V
    * Inspecionar anterior : Q
    * Inspecionar próximo : W
    * Gabarito de feições : G
    * Liga/Desliga todas as labels : L
    * Ferramenta de Aquisição à Mão Livre : F
    * Remodelar feições mão livre : Shift+R

* Adicionado bloqueio que não permite o usuário executar rotinas do FME se possuir camadas não salvas.

* O SAP agora configura as seguintes opções:
    * Snap vem habilitado por padrão com 10 pixel e somente Vértice.
    * Modificação na espessura da linha do rubber band ao digitalizar.
    * Modificação na transparência da cor da linha e de polígono de rubber band.
    * Marcadores de nó modificado para Círculo semi-transparente.
    * Modificada as escalas padrão do QGIS para: 1:250000,1:100000,1:50000,1:25000,1:10000,1:5000,1:2000,1:1000,1:500,1:250

* Corrigida interface com textos longs de requisitos.

* Corrigido bug no aviso para o usuário salvar as alterações. O aviso após 5 minutos sem o usuário salvar, e caso não salve o aviso muda a peridiocidade para 2.5 minutos.

* Corrigido bug na exibição de rotinas.

* A árvore de camadas é carregada aberta por default.

* Removido botão de _carregar somente camadas com feições_ no modo remoto.

* Corrigido bug na busca textual de camadas no modo local.

* Insumos são carregados com o sistema de coordenadas informado no SAP. Este caso é especialmente útil para ECW, onde o operador tinha que definir o sistema de coordenadas manualmente.

* Corrido bug de download de insumos em pastas com nome contendo caracteres especiais.

* Corrigido bug no menu de classificação que inseria strings vazias em vez do valor Nulo.

* Resolvido bug ao cancelar o download de insumos.

* Resolvido bug em que a aba _Dados_ requisitava repetidamente as informações de produção.


Para maiores informações sobre o SAP verifique a [Wiki](https://github.com/1cgeo/sap/wiki)
