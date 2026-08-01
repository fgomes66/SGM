from dataclasses import FrozenInstanceError, replace
from datetime import date
from decimal import Decimal
import pytest
from sgm.desktop import ContratoTrabalho, ControladorDesktop, DadosContratoFormulario, RepositorioProcessosJSON, TipoContratoTrabalho
from tests.unitarios.test_cadastro_processo_desktop_0_9_3_b import formulario_valido

def form():
 return DadosContratoFormulario(data_admissao='2020-01-10',data_desligamento='2024-05-20',tipo_contrato='INDETERMINADO',cargo='Analista',funcao='Analista Contábil',cbo='2522-10',salario_inicial='3500,00',jornada_semanal_horas='44',divisor_jornada='220',motivo_desligamento='Dispensa sem justa causa',sindicato='Sindicato X',norma_coletiva='CCT 2024')

def test_01_padrao(): assert DadosContratoFormulario().jornada_semanal_horas=='44'
def test_02_valido(): assert form().validar()==()
def test_03_cria(): assert isinstance(form().criar_contrato(),ContratoTrabalho)
def test_04_data(): assert form().criar_contrato().data_admissao==date(2020,1,10)
def test_05_salario(): assert form().criar_contrato().salario_inicial==Decimal('3500.00')
def test_06_tipo(): assert form().criar_contrato().tipo_contrato==TipoContratoTrabalho.INDETERMINADO
def test_07_data_invalida(): assert replace(form(),data_admissao='10/01/2020').validar()
def test_08_desligamento_anterior(): assert replace(form(),data_desligamento='2019-01-01').validar()
def test_09_salario_zero(): assert replace(form(),salario_inicial='0').validar()
def test_10_jornada_zero(): assert replace(form(),jornada_semanal_horas='0').validar()
def test_11_jornada_excessiva(): assert replace(form(),jornada_semanal_horas='61').validar()
def test_12_divisor_zero(): assert replace(form(),divisor_jornada='0').validar()
def test_13_cargo_vazio(): assert replace(form(),cargo='').validar()
def test_14_funcao_vazia(): assert replace(form(),funcao='').validar()
def test_15_opcionais_none(): assert replace(form(),cbo='',sindicato='',norma_coletiva='').criar_contrato().cbo is None
def test_16_imutavel():
 c=form().criar_contrato()
 with pytest.raises(FrozenInstanceError): c.cargo='Outro'
def test_17_controlador_registra():
 c=ControladorDesktop(); assert c.registrar_contrato(form())==(); assert c.estado.contrato_trabalho is not None
def test_18_controlador_rejeita():
 c=ControladorDesktop(); assert c.registrar_contrato(DadosContratoFormulario())
def test_19_persistencia(tmp_path):
 repo=RepositorioProcessosJSON(tmp_path); c=ControladorDesktop(repositorio=repo); c.novo_processo('CASO-C'); c.registrar_identificacao(formulario_valido()); c.registrar_contrato(form()); c.salvar(); d=repo.carregar('CASO-C'); assert d.contrato.cargo=='Analista'
def test_20_carregamento_controlador(tmp_path):
 repo=RepositorioProcessosJSON(tmp_path); c=ControladorDesktop(repositorio=repo); c.novo_processo('CASO-C'); c.registrar_identificacao(formulario_valido()); c.registrar_contrato(form()); c.salvar(); outro=ControladorDesktop(repositorio=repo); outro.abrir('CASO-C'); assert outro.estado.contrato_trabalho.funcao=='Analista Contábil'
def test_21_schema_novo(tmp_path):
 repo=RepositorioProcessosJSON(tmp_path); c=ControladorDesktop(repositorio=repo); c.novo_processo('CASO-C'); c.registrar_identificacao(formulario_valido()); c.registrar_contrato(form()); p=c.salvar(); assert '"schema": 1' in p.read_text(encoding='utf-8')
def test_22_arquivo_antigo_compativel(tmp_path):
 import json
 repo=RepositorioProcessosJSON(tmp_path); dados={"schema":1,"referencia":"ANTIGO","identificacao":{"orgao_julgador":{"tribunal":"TRT","regiao_trt":1,"vara":"Vara","municipio":"Rio","uf":"RJ"},"numero_processo":"0001234-55.2024.5.01.0007","classe_processual":"Classe","reclamante":"Autor","reclamada":"Ré","magistrado":None,"perito":None,"assistente_reclamante":None,"assistente_reclamada":None,"advogado_reclamante":None,"advogado_reclamada":None}}
 repo.caminho_para('ANTIGO').write_text(json.dumps(dados),encoding='utf-8'); assert repo.carregar('ANTIGO').contrato is None
def test_23_preserva_observacoes(tmp_path):
 repo=RepositorioProcessosJSON(tmp_path); c=ControladorDesktop(repositorio=repo); c.novo_processo('CASO-C'); c.registrar_identificacao(formulario_valido()); c.registrar_contrato(replace(form(),observacoes='Teste')); c.salvar(); assert repo.carregar('CASO-C').contrato.observacoes=='Teste'
def test_24_preserva_processo_ao_registrar():
 c=ControladorDesktop(); c.registrar_identificacao(formulario_valido()); i=c.estado.identificacao_processo; c.registrar_contrato(form()); assert c.estado.identificacao_processo==i
def test_25_contrato_nao_muda_secao():
 from sgm.desktop import SecaoDesktop
 c=ControladorDesktop(); c.navegar(SecaoDesktop.CONTRATO); c.registrar_contrato(form()); assert c.estado.secao_atual==SecaoDesktop.CONTRATO
