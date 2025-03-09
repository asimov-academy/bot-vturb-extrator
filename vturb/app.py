import os
import sys
import traceback
from dotenv import load_dotenv

from browser import Browser
from files import move_csv_files
from logger import (
    log, log_section, start_timer, end_timer, 
    LogType, format_number, get_log_filename, current_time
)
from execution_manager import ExecutionManager


def main():
    # Início do programa
    start_timer("execucao_total")
    
    # Inicializa o gerenciador de execução
    manager = ExecutionManager()
    
    # Limpa registros antigos (mais de 7 dias)
    manager.clear_old_records()
    
    # Verifica se deve executar
    if not manager.should_execute():
        return
    
    log_section(f"INICIANDO EXECUÇÃO EM {current_time()}")
    
    try:
        log("Carregando variáveis de ambiente...", LogType.STEP)
        start_timer("env_loading")
        load_dotenv()
        log("Variáveis de ambiente carregadas", LogType.SUCCESS, show_time=True, operation_name="env_loading")

        log("Inicializando o navegador...", LogType.STEP)
        start_timer("browser_init")
        browser = Browser(headless=True)
        browser.open()
        log("Navegador inicializado com sucesso", LogType.SUCCESS, show_time=True, operation_name="browser_init")

        # Login
        log("Navegando para a página de login...", LogType.STEP)
        start_timer("login_process")
        browser.visit('https://login.vturb.com/signin')

        log("Preenchendo credenciais...", LogType.STEP, indent_level=1)
        browser.find_element_by_xpath("//input[@name='email']").send_keys(os.getenv('EMAIL_LOGIN'))
        browser.find_element_by_xpath("//input[@name='password']").send_keys(os.getenv('PASSWORD_LOGIN'))

        log("Clicando no botão de login...", LogType.STEP, indent_level=1)
        browser.find_element_by_xpath("//button[@type='button']").click()

        # Verifica se já está logado
        log("Aguardando página principal carregar...", LogType.STEP, indent_level=1)
        browser.wait_for_element("//tr[td[contains(@title, 'VSL') and contains(@title, 'IA')]]")
        browser.wait(3)
        log("Login realizado com sucesso!", LogType.SUCCESS, show_time=True, operation_name="login_process")

        # Conta quantas pastas existem de videos
        log("Identificando pastas de vídeos...", LogType.STEP)
        start_timer("folder_count")
        all_folders = browser.find_elements_by_xpath("//tr[td[contains(@title, 'VSL') and contains(@title, 'IA')]]")
        folder_count = len(all_folders)
        log(f"Total de pastas encontradas: {folder_count}", LogType.SUCCESS, show_time=True, operation_name="folder_count")

        # Exibe os textos de cada pasta encontrada
        log("Listagem de pastas:", LogType.INFO)
        for idx, folder_el in enumerate(all_folders):
            try:
                folder_text = folder_el.text.replace("\n", " - ")
                views_downloads = folder_text.split(" ")[-2:]
                views = format_number(views_downloads[-2])
                downloads = format_number(views_downloads[-1])
                folder_name = " ".join(folder_text.split(" ")[:-2])
                log(f"Pasta {idx+1}/{folder_count}: {folder_name}", LogType.INFO, indent_level=1)
            except:
                folder_text = "N/A"
                log(f"Pasta {idx+1}/{folder_count}: {folder_text}", LogType.INFO, indent_level=1)

        # Itera sobre todas as pastas que encontrar
        for index in range(folder_count):
            log_section(f"PROCESSANDO PASTA {index+1} DE {folder_count}")
            
            # Esperando a pagina carregar o elemento
            log("Aguardando carregamento da lista de pastas...", LogType.STEP)
            start_timer("folder_load")
            browser.wait_for_element("//tr[td[contains(@title, 'VSL') and contains(@title, 'IA')]]")
            log("Lista de pastas carregada", LogType.SUCCESS, show_time=True, operation_name="folder_load")

            # Mostra quantas pastas ainda existem nesse momento
            current_folders = browser.find_elements_by_xpath("//tr[td[contains(@title, 'VSL') and contains(@title, 'IA')]]")
            log(f"Pastas disponíveis no momento: {len(current_folders)}", LogType.INFO)

            # Tenta exibir o texto de cada pasta novamente
            log("Pastas atuais:", LogType.INFO)
            for i, f_el in enumerate(current_folders):
                try: 
                    txt = f_el.text.replace("\n", " - ")
                    parts = txt.split(" ")
                    if len(parts) >= 2:
                        views_downloads = parts[-2:]
                        views = format_number(views_downloads[-2])
                        downloads = format_number(views_downloads[-1])
                        folder_name = " ".join(parts[:-2])
                        log(f"Pasta {i+1}: '{folder_name}'", LogType.INFO, indent_level=1)
                    else:
                        log(f"Pasta {i+1}: '{txt}'", LogType.INFO, indent_level=1)
                except:
                    txt = "N/A"
                    log(f"Pasta {i+1}: '{txt}'", LogType.INFO, indent_level=1)

            try:
                current_folder = current_folders[index]
                log(f"Selecionando pasta com índice [{index}]...", LogType.STEP)
            except IndexError:
                log(f"Não existe pasta com índice [{index}]. Encerrando processamento de pastas.", LogType.ERROR)
                break

            # Mostra o texto do folder selecionado
            try:
                cf_text = current_folder.text.replace("\n", " - ")
                log(f"Pasta selecionada: '{cf_text}'", LogType.SUCCESS)
            except:
                cf_text = "N/A"
                log(f"Não foi possível obter o texto da pasta selecionada.", LogType.WARNING)

            log("Clicando duas vezes na pasta...", LogType.STEP)
            start_timer("folder_click")
            browser.double_click(current_folder)
            log("Clique duplo realizado", LogType.SUCCESS, show_time=True, operation_name="folder_click")

            # Verifica se existe videos dentro da pasta
            log("Verificando se existem vídeos dentro da pasta...", LogType.STEP)
            start_timer("video_check")
            video = browser.wait_for_element("//tr[td[contains(@title, 'VSL') and contains(@title, 'IA')]]", timeout=2)
            if not video:
                log("Nenhum vídeo encontrado na pasta. Voltando para a lista de pastas.", LogType.WARNING, show_time=True, operation_name="video_check")
                browser.visit('https://app.vturb.com/folders')
                continue
            else:
                log("Vídeos encontrados na pasta!", LogType.SUCCESS, show_time=True, operation_name="video_check")

            # Pega a quantidade de videos dentro da pasta
            videos_in_pasta = browser.find_elements_by_xpath("//tr[td[contains(@title, 'VSL') and contains(@title, 'IA')]]")
            videos_count = len(videos_in_pasta)
            log(f"Total de vídeos na pasta: {videos_count}", LogType.INFO)

            # Lista os vídeos encontrados
            log("Vídeos disponíveis:", LogType.INFO)
            for idxv, vid_el in enumerate(videos_in_pasta):
                try:
                    vid_text = vid_el.text.replace("\n", " - ")
                    views_downloads = vid_text.split(" ")[-2:]
                    views = format_number(views_downloads[-2])
                    downloads = format_number(views_downloads[-1])
                    video_name = " ".join(vid_text.split(" ")[:-2])
                    log(f"Vídeo {idxv+1}/{videos_count}: {video_name}", LogType.INFO, indent_level=1)
                except:
                    vid_text = "N/A"
                    log(f"Vídeo {idxv+1}/{videos_count}: '{vid_text}'", LogType.INFO, indent_level=1)

            # Itera sobre todos os videos que encontrar
            for video_index in range(videos_count):
                log_section(f"PROCESSANDO VÍDEO {video_index+1} DE {videos_count}", level=2)

                # Re-coleta a lista de vídeos
                log("Atualizando lista de vídeos disponíveis...", LogType.STEP)
                updated_videos = browser.find_elements_by_xpath("//tr[td[contains(@title, 'VSL') and contains(@title, 'IA')]]")
                log(f"Vídeos disponíveis no momento: {len(updated_videos)}", LogType.INFO)

                # Tenta mostrar o texto de cada video de novo
                log("Vídeos atuais:", LogType.INFO)
                for i2, uv in enumerate(updated_videos):
                    try:
                        uv_text = uv.text.replace("\n", " - ")
                        parts = uv_text.split(" ")
                        if len(parts) >= 2:
                            views_downloads = parts[-2:]
                            views = format_number(views_downloads[-2])
                            downloads = format_number(views_downloads[-1])
                            video_name = " ".join(parts[:-2])
                            log(f"Vídeo {i2+1}: '{video_name}'", LogType.INFO, indent_level=1)
                        else:
                            log(f"Vídeo {i2+1}: '{uv_text}'", LogType.INFO, indent_level=1)
                    except:
                        uv_text = "N/A"
                        log(f"Vídeo {i2+1}: '{uv_text}'", LogType.INFO, indent_level=1)

                try:
                    video_current = updated_videos[video_index]
                    log(f"Selecionando vídeo com índice [{video_index}]...", LogType.STEP)
                except IndexError:
                    log(f"Não existe vídeo com índice [{video_index}]. Pulando para o próximo vídeo.", LogType.ERROR)
                    continue

                # Mostra texto do vídeo selecionado
                try:
                    vc_text = video_current.text.replace("\n", " - ")
                    log(f"Vídeo selecionado: '{vc_text}'", LogType.SUCCESS)
                except:
                    vc_text = "N/A"
                    log("Não foi possível obter o texto do vídeo selecionado.", LogType.WARNING)

                log("Clicando duas vezes no vídeo...", LogType.STEP)
                start_timer("video_click")
                browser.double_click(video_current)
                browser.wait(2)
                log("Clique duplo realizado", LogType.SUCCESS, show_time=True, operation_name="video_click")

                # Verifica se entrou no video, caso não tenta de novo
                log("Verificando se a página do vídeo foi carregada...", LogType.STEP)
                start_timer("video_page")
                analytics_element = browser.wait_for_element("//a[contains(@href, 'analytics')]", timeout=3)
                if not analytics_element:
                    log("Falha ao acessar a página do vídeo. Tentando clicar novamente...", LogType.WARNING)
                    try:
                        video_current = browser.find_elements_by_xpath("//tr[td[contains(@title, 'VSL') and contains(@title, 'IA')]]")[video_index]
                        browser.double_click(video_current)
                        log("Clique duplo realizado novamente.", LogType.INFO, indent_level=1)
                    except:
                        log("Falha ao tentar clicar no vídeo pela segunda vez.", LogType.ERROR, indent_level=1)
                    browser.wait(2)
                else:
                    log("Página do vídeo carregada com sucesso!", LogType.SUCCESS, show_time=True, operation_name="video_page")

                # acessa a pagina de analise do video
                log("Tentando acessar a página de analytics...", LogType.STEP)
                start_timer("analytics_page")
                analytics_element = browser.wait_for_element("//a[contains(@href, 'analytics')]", timeout=3)
                if analytics_element:
                    analytics_element.click()
                    log("Navegando para a página de analytics.", LogType.SUCCESS)
                else:
                    log("Elemento de analytics não encontrado.", LogType.ERROR)
                    end_timer("analytics_page")

                # verifica se a pagina de analise entrou
                log("Verificando se a página de analytics foi carregada...", LogType.STEP, indent_level=1)
                traffic_element = browser.wait_for_element("//a[contains(@href, 'traffic')]", timeout=3)
                if not traffic_element:
                    log("Falha ao carregar a página de analytics. Tentando novamente...", LogType.WARNING, indent_level=1)
                    if analytics_element:
                        analytics_element.click()
                        log("Clique em analytics realizado novamente.", LogType.INFO, indent_level=2)
                    browser.wait(2)
                else:
                    log("Página de analytics carregada com sucesso!", LogType.SUCCESS, show_time=True, operation_name="analytics_page", indent_level=1)
                
                # acessa a pagina de analise de trafego do video
                log("Tentando acessar a página de tráfego...", LogType.STEP)
                start_timer("traffic_page")
                traffic_element = browser.wait_for_element("//a[contains(@href, 'traffic')]", timeout=3)
                if traffic_element:
                    traffic_element.click()
                    log("Navegando para a página de tráfego.", LogType.SUCCESS)
                else:
                    log("Elemento de tráfego não encontrado.", LogType.ERROR)
                    end_timer("traffic_page")

                # verifica se entrou na pagina de trafego
                log("Verificando se a página de tráfego foi carregada...", LogType.STEP, indent_level=1)
                utm_dropdown_element = browser.wait_for_element("//button[@role='combobox'][1]")
                if not utm_dropdown_element and traffic_element:
                    log("Falha ao carregar a página de tráfego. Tentando novamente...", LogType.WARNING, indent_level=1)
                    traffic_element.click()
                    browser.wait(2)
                else:
                    log("Página de tráfego carregada com sucesso!", LogType.SUCCESS, show_time=True, operation_name="traffic_page", indent_level=1)
                
                # abre o dropdown e seleciona a opção utm_content
                browser.wait(5)
                log("Tentando abrir o dropdown de UTM...", LogType.STEP)
                start_timer("utm_dropdown")
                try:
                    cb = browser.wait_for_element("//button[@role='combobox'][1]")
                    if cb:
                        cb.click()
                        log("Dropdown de UTM aberto com sucesso.", LogType.SUCCESS, show_time=True, operation_name="utm_dropdown")
                    else:
                        log("Dropdown não encontrado pelo wait_for_element. Tentando com find_element_by_xpath...", LogType.WARNING)
                        browser.find_element_by_xpath("//button[@role='combobox'][1]").click()
                        log("Dropdown de UTM aberto via find_element_by_xpath.", LogType.SUCCESS)
                    browser.wait(1)
                except Exception as e:
                    log(f"ERRO ao tentar abrir o dropdown de UTM: {str(e)}", LogType.ERROR)
                    try:
                        browser.find_element_by_xpath("//button[@role='combobox'][1]").click()
                        log("Segunda tentativa de abrir o dropdown realizada.", LogType.INFO)
                    except:
                        log("Falha na segunda tentativa de abrir o dropdown.", LogType.ERROR)
                        raise Exception(f"ERRO ao selecionar o dropdown: {str(e)}")

                # clica em utm_content
                log("Tentando selecionar a opção utm_content...", LogType.STEP)
                start_timer("utm_select")
                try:
                    browser.find_element_by_xpath("//span[contains(., 'utm_content')]").click()
                    log("Opção utm_content selecionada com sucesso.", LogType.SUCCESS, show_time=True, operation_name="utm_select")
                except Exception as e:
                    log(f"ERRO ao selecionar utm_content: {str(e)}", LogType.ERROR)
                    raise Exception(f"ERRO ao selecionar utm_content: {str(e)}")

                browser.wait(2)
                
                # clica no dropdown para escolher a opção da extensão do arquivo para download
                log("Tentando abrir o menu de download de métricas...", LogType.STEP)
                start_timer("download_menu")
                try:
                    browser.wait_for_element("//button[strong[contains(text(), 'Baixar Métricas')]]").click()
                    log("Menu de 'Baixar Métricas' aberto com sucesso.", LogType.SUCCESS, show_time=True, operation_name="download_menu")
                except Exception as e:
                    log(f"ERRO ao abrir menu de 'Baixar Métricas': {str(e)}", LogType.ERROR)

                browser.wait(1)
                log("Tentando selecionar a opção CSV...", LogType.STEP)
                start_timer("csv_select")
                try:
                    browser.wait_for_element("//button[.//span[contains(text(), 'CSV')]]").click()
                    log("Opção CSV selecionada. Iniciando download.", LogType.SUCCESS, show_time=True, operation_name="csv_select")
                except Exception as e:
                    log(f"ERRO ao selecionar opção CSV: {str(e)}", LogType.ERROR)

                log("Aguardando conclusão do download...", LogType.STEP)
                start_timer("download")
                browser.wait(4)
                log("Tempo de espera para download concluído", LogType.SUCCESS, show_time=True, operation_name="download")

                # pega o nome do video
                log("Obtendo o nome do vídeo para organizar os arquivos...", LogType.STEP)
                try:
                    folder_name_el = browser.find_element_by_xpath("//span[contains(@title, 'VSL IA')]")
                    folder_name = folder_name_el.text
                    log(f"Nome do vídeo obtido: '{folder_name}'", LogType.SUCCESS)
                except Exception as e:
                    folder_name = "VIDEO_NAME_NOT_FOUND"
                    log(f"ERRO ao obter o nome do vídeo: {str(e)}", LogType.ERROR)

                log(f"Movendo arquivos CSV para a pasta ./analytics/{folder_name}...", LogType.STEP)
                start_timer("move_files")
                try:
                    move_csv_files(
                        source_folder="/home/samuel/Downloads",
                        destination_folder=f"./analytics/{folder_name}"
                    )
                    log("Arquivos CSV movidos com sucesso.", LogType.SUCCESS, show_time=True, operation_name="move_files")
                except Exception as e:
                    log(f"ERRO ao mover arquivos CSV: {str(e)}", LogType.ERROR)
                
                # volta as paginas necessarias para começar o loop outra vez
                log("Retornando para a lista de vídeos (history.go(-3))...", LogType.STEP)
                start_timer("return_navigation")
                browser.driver.execute_script("window.history.go(-3)")
                browser.wait(2)

                # se ainda encontrar analytics, volta -1
                log("Verificando se retornou corretamente...", LogType.STEP)
                if (
                    browser.wait_for_element("//a[contains(@href, 'analytics')]", timeout=3) 
                    and 
                    browser.wait_for_element("//button[.//span[contains(text(), 'Download')]]", timeout=3)
                ):
                    log("Ainda na página de analytics. Voltando mais uma vez (history.go(-1))...", LogType.WARNING)
                    browser.driver.execute_script("window.history.go(-1)")
                    browser.wait(2)
                else:
                    log("Retorno para a lista de vídeos realizado com sucesso.", LogType.SUCCESS, show_time=True, operation_name="return_navigation")

                log(f"VÍDEO {video_index+1} PROCESSADO COM SUCESSO!", LogType.SUCCESS)

            # volta para a pagina de pastas para iniciar mais uma pasta na lista
            log("Retornando para a página principal de pastas...", LogType.STEP)
            start_timer("return_to_folders")
            browser.visit('https://app.vturb.com/folders')
            log("Retorno para página principal realizado com sucesso", LogType.SUCCESS, show_time=True, operation_name="return_to_folders")
            log(f"PASTA {index+1} PROCESSADA COM SUCESSO!", LogType.SUCCESS)

        # Finalização
        log_section("RESUMO DA EXECUÇÃO")
        total_time = end_timer("execucao_total")
        hours, remainder = divmod(total_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_format = f"{int(hours):02d}h {int(minutes):02d}m {int(seconds):02d}s"

        log(f"Tempo total de execução: {time_format}", LogType.SUCCESS)
        log(f"Pastas processadas: {folder_count}", LogType.INFO)
        log(f"Log completo salvo em: {get_log_filename()}", LogType.INFO)
        log("EXECUÇÃO FINALIZADA COM SUCESSO!", LogType.SUCCESS)
        
        # Registra execução bem-sucedida
        manager.register_execution(success=True)
        
        # Fecha o navegador
        browser.close()
        
    except Exception as e:
        log(f"ERRO CRÍTICO NA EXECUÇÃO: {str(e)}", LogType.ERROR)
        log(f"Detalhes: {traceback.format_exc()}", LogType.ERROR)
        
        # Registra execução mal-sucedida
        manager.register_execution(success=False)


if __name__ == "__main__":
    main()