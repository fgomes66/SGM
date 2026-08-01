from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, ttk
from sgm.desktop.aplicacao import ControladorDesktop, DadosContratoFormulario, EstadoDesktop, TipoContratoTrabalho

class TelaContrato(ttk.Frame):
    CAMPOS=(("data_admissao","Data de admissão (AAAA-MM-DD)"),("data_desligamento","Data de desligamento — opcional"),("cargo","Cargo"),("funcao","Função"),("cbo","CBO — opcional"),("salario_inicial","Salário inicial"),("jornada_semanal_horas","Jornada semanal (horas)"),("divisor_jornada","Divisor da jornada"),("motivo_desligamento","Motivo do desligamento — opcional"),("sindicato","Sindicato — opcional"),("norma_coletiva","CCT/ACT — opcional"),("observacoes","Observações — opcional"))
    def __init__(self,mestre,controlador):
        super().__init__(mestre,padding=20); self.controlador=controlador; self.columnconfigure(1,weight=1)
        ttk.Label(self,text="Cadastro do Contrato de Trabalho",font=("Segoe UI",18,"bold")).grid(row=0,column=0,columnspan=2,sticky='w',pady=(0,14))
        self._vars={}; padrao=DadosContratoFormulario()
        ttk.Label(self,text="Tipo de contrato").grid(row=1,column=0,sticky='w',padx=(0,12),pady=4)
        self._tipo=tk.StringVar(value=padrao.tipo_contrato)
        ttk.Combobox(self,textvariable=self._tipo,state='readonly',values=[x.value for x in TipoContratoTrabalho]).grid(row=1,column=1,sticky='ew',pady=4)
        for i,(campo,rotulo) in enumerate(self.CAMPOS,start=2):
            ttk.Label(self,text=rotulo).grid(row=i,column=0,sticky='w',padx=(0,12),pady=4)
            v=tk.StringVar(value=getattr(padrao,campo)); self._vars[campo]=v
            ttk.Entry(self,textvariable=v).grid(row=i,column=1,sticky='ew',pady=4)
        linha=len(self.CAMPOS)+2
        ttk.Button(self,text="Validar e registrar",command=self._registrar).grid(row=linha,column=1,sticky='e',pady=(16,0))
        self._msg=ttk.Label(self,text='',wraplength=760); self._msg.grid(row=linha+1,column=0,columnspan=2,sticky='w',pady=(10,0))
    def _form(self): return DadosContratoFormulario(tipo_contrato=self._tipo.get(),**{k:v.get() for k,v in self._vars.items()})
    def _registrar(self):
        erros=self.controlador.registrar_contrato(self._form())
        if erros:
            txt='\n'.join('• '+e for e in erros); self._msg.configure(text=txt); messagebox.showerror('Contrato',txt,parent=self)
        else: self._msg.configure(text='Contrato registrado com sucesso.')
    def carregar_estado(self,estado: EstadoDesktop):
        c=estado.contrato_trabalho
        if not c: return
        self._tipo.set(c.tipo_contrato.value)
        dados={"data_admissao":c.data_admissao.isoformat(),"data_desligamento":c.data_desligamento.isoformat() if c.data_desligamento else '',"cargo":c.cargo,"funcao":c.funcao,"cbo":c.cbo or '',"salario_inicial":str(c.salario_inicial),"jornada_semanal_horas":str(c.jornada_semanal_horas),"divisor_jornada":str(c.divisor_jornada),"motivo_desligamento":c.motivo_desligamento or '',"sindicato":c.sindicato or '',"norma_coletiva":c.norma_coletiva or '',"observacoes":c.observacoes or ''}
        for k,v in dados.items(): self._vars[k].set(v)
