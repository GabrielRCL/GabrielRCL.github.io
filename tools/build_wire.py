"""Generate partials/wire.html: the "What goes over the wire" section.

Every sample follows the shapes of the production integrations (fields, order, positions),
with fictitious data: CNAB 240 segment P (Sicoob layout), NFS-e Nacional DPS signed with XMLDSig,
a WhatsApp coexistence echo, a Zabbix host.get result as the CMDB reads it, and MCP tools/call.
"""
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "partials", "wire.html")


# ---------------------------------------------------------------- CNAB 240
def cnab_segment_p():
    f = [  # (label_en, label_pt, value)  -- widths follow the Sicoob wizard, positions 001-240
        ("Bank", "Banco", "756"),
        ("Batch", "Lote", "0001"),
        ("Record type", "Tipo de registro", "3"),
        ("Sequence", "Sequencial", "00001"),
        ("Segment", "Segmento", "P"),
        (None, None, " "),
        ("Movement 01 = new title", "Movimento 01 = entrada de título", "01"),
        ("Branch", "Agência", "04321"),
        (None, None, "0"),
        ("Account", "Conta", "000000123456"),
        (None, None, "7"),
        (None, None, " "),
        ("Our number", "Nosso número", "0000012345" + "01014     "),
        (None, None, "1" + "0" + " " + "2" + "2"),
        ("Document", "Documento", "NF-000482".ljust(15)),
        ("Due date", "Vencimento", "10102026"),
        ("Amount (cents)", "Valor (centavos)", "150000".zfill(15)),
        (None, None, "00000" + " " + "04" + "N"),
        ("Issue date", "Emissão", "26092026"),
        (None, None, "1" + "11102026" + "33".zfill(15) + "0" + "00000000" + "0" * 15 + "0" * 15 + "0" * 15),
        ("Your reference", "Sua referência", "INV/2026/00482".ljust(25)),
        (None, None, "3" + "00" + "0" + "   " + "09" + "0000000000" + " "),
    ]
    line = "".join(v for _, _, v in f)
    assert len(line) == 240, len(line)
    return f, line


def cnab_html():
    fields, line = cnab_segment_p()
    spans, rows, pos = [], [], 1
    for i, (en, pt, v) in enumerate(fields):
        end = pos + len(v) - 1
        txt = html.escape(v).replace(" ", "&#183;")
        if en:
            spans.append(f'<span class="fld f{len(rows) % 6}" title="{pos:03d}-{end:03d} {html.escape(en)}">{txt}</span>')
            rows.append(f'<tr><td>{pos:03d}–{end:03d}</td><td><span class="en">{html.escape(en)}</span><span class="pt">{html.escape(pt)}</span></td><td><code>{html.escape(v.strip()) or "·"}</code></td></tr>')
        else:
            spans.append(f'<span class="gap">{txt}</span>')
        pos = end + 1
    return (
        '<div class="wire-code cnab" tabindex="0"><pre>' + "".join(spans) + "</pre></div>"
        '<table class="fields"><thead><tr><th><span class="en">Positions</span><span class="pt">Posições</span></th>'
        '<th><span class="en">Field</span><span class="pt">Campo</span></th><th><span class="en">Value</span><span class="pt">Valor</span></th></tr></thead><tbody>'
        + "".join(rows) + "</tbody></table>"
    )


# ---------------------------------------------------------------- NFS-e DPS
def dps_xml():
    cnpj_prest, cnpj_toma, mun = "11222333000181", "44555666000134", "3205200"
    dps_id = "DPS" + mun + "2" + cnpj_prest + "1".zfill(5) + "482".zfill(15)
    assert len(dps_id) == 45
    return f"""<DPS xmlns="http://www.sped.fazenda.gov.br/nfse" versao="1.01">
  <infDPS Id="{dps_id}">
    <tpAmb>2</tpAmb>
    <dhEmi>2026-09-26T10:30:00-03:00</dhEmi>
    <verAplic>1.0</verAplic>
    <serie>1</serie>
    <nDPS>482</nDPS>
    <dCompet>2026-09-26</dCompet>
    <tpEmit>1</tpEmit>
    <cLocEmi>{mun}</cLocEmi>
    <prest>
      <CNPJ>{cnpj_prest}</CNPJ>
      <regTrib><opSimpNac>1</opSimpNac><regEspTrib>0</regEspTrib></regTrib>
    </prest>
    <toma>
      <CNPJ>{cnpj_toma}</CNPJ>
      <xNome>Cliente Exemplo Ltda</xNome>
    </toma>
    <serv>
      <locPrest><cLocPrestacao>{mun}</cLocPrestacao></locPrest>
      <cServ>
        <cTribNac>010701</cTribNac>
        <xDescServ>Suporte técnico em sistema de gestão</xDescServ>
      </cServ>
    </serv>
    <valores>
      <vServPrest><vServ>1500.00</vServ></vServPrest>
      <trib>
        <tribMun><tribISSQN>1</tribISSQN><tpRetISSQN>1</tpRetISSQN></tribMun>
        <totTrib><indTotTrib>0</indTotTrib></totTrib>
      </trib>
    </valores>
  </infDPS>
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <SignedInfo>
      <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
      <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
      <Reference URI="#{dps_id}">
        <Transforms>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
          <Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
        </Transforms>
        <DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
        <DigestValue>q3N0…Zk8=</DigestValue>
      </Reference>
    </SignedInfo>
    <SignatureValue>hL9f…w2Q==</SignatureValue>
    <KeyInfo><X509Data><X509Certificate>MIIH…A1…</X509Certificate></X509Data></KeyInfo>
  </Signature>
</DPS>"""


TAG = re.compile(r'(&lt;/?)([A-Za-z0-9:]+)((?:\s+[A-Za-z:]+="[^"]*")*)(\s*/?&gt;)')
ATTR = re.compile(r'([A-Za-z:]+)=("[^"]*")')


def hl_xml(src):
    """Highlight tags, attributes and text in one pass per token, so no pass rewrites another's markup."""
    def tag(m):
        attrs = ATTR.sub(r'<span class="a">\1</span>=<span class="s">\2</span>', m.group(3))
        return f'{m.group(1)}<span class="t">{m.group(2)}</span>{attrs}{m.group(4)}'

    out = []
    for line in html.escape(src, quote=False).split("\n"):
        pieces, last = [], 0
        for m in TAG.finditer(line):
            text = line[last:m.start()]
            pieces.append(f'<span class="v">{text}</span>' if text.strip() else text)
            pieces.append(tag(m))
            last = m.end()
        pieces.append(line[last:])
        out.append("".join(pieces))
    return "\n".join(out)


# ---------------------------------------------------------------- JSON samples
ECHO = """{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "102030405060708",
    "changes": [{
      "field": "smb_message_echoes",
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {
          "display_phone_number": "5527999990000",
          "phone_number_id": "109876543210987"
        },
        "message_echoes": [{
          "from": "5527999990000",
          "to": "5527988887777",
          "id": "wamid.HBgMNTUyNzk4ODg4Nzc3NxUCABEY…",
          "timestamp": "1790412345",
          "type": "text",
          "text": { "body": "Seu pedido saiu para entrega." }
        }]
      }
    }]
  }]
}"""

ZABBIX = """{
  "jsonrpc": "2.0",
  "result": [{
    "hostid": "10542",
    "host": "prod-web-01",
    "name": "PROD-WEB-01 (VM)",
    "status": "0",
    "description": "Customer portal, web tier",
    "interfaces": [{
      "interfaceid": "31", "ip": "10.10.20.15", "dns": "",
      "port": "10050", "type": "1", "main": "1", "useip": "1"
    }],
    "groups": [{ "groupid": "42", "name": "Production / Web" }],
    "tags": [
      { "tag": "category", "value": "Server" },
      { "tag": "impact", "value": "High" }
    ]
  }],
  "id": 1
}"""

MCP = """→ {"jsonrpc": "2.0", "id": 7, "method": "tools/call",
   "params": {"name": "search_read", "arguments": {
     "model": "helpdesk.ticket",
     "domain": [["stage_id.fold", "=", false]],
     "fields": ["name", "priority", "user_id"], "limit": 5}}}

← {"jsonrpc": "2.0", "id": 7, "result": {"content": [{"type": "text",
   "text": "[{\\"id\\":29,\\"name\\":\\"VPN down for northern branch\\",\\"priority\\":\\"2\\",\\"user_id\\":[2,\\"Mitchell Admin\\"]}]"}]}}

→ {"jsonrpc": "2.0", "id": 8, "method": "tools/call",
   "params": {"name": "search_read", "arguments": {
     "model": "hr.employee", "fields": ["name", "job_title"]}}}

← {"jsonrpc": "2.0", "id": 8, "result": {"isError": true, "content": [{"type": "text",
   "text": "'hr.employee': This information is not available through the assistant. Ask an administrator to enable the permission."}]}}"""


def hl_json(src):
    s = html.escape(src, quote=False)
    s = re.sub(r'("(?:[^"\\]|\\.)*")(\s*:)', r'<span class="a">\1</span>\2', s)
    s = re.sub(r'(:\s*|\[\s*|,\s*)("(?:[^"\\]|\\.)*")', r'\1<span class="s">\2</span>', s)
    s = re.sub(r"\b(true|false|null)\b", r'<span class="v">\1</span>', s)
    s = re.sub(r"^(→|←)", r'<span class="dir">\1</span>', s, flags=re.M)
    return s


def code(src, kind):
    body = hl_xml(src) if kind == "xml" else hl_json(src)
    return f'<div class="wire-code" tabindex="0"><pre>{body}</pre></div>'


PANELS = [
    ("cnab", "lu-landmark", "CNAB 240", "CNAB 240", cnab_html(),
     ["Segment P of a Sicoob remittance file: one boleto per record, every field at a fixed position, exactly 240 characters.",
      "Amounts go in cents without a decimal point; dates as DDMMYYYY.",
      "Inter and Itaú are integrated through their REST APIs (mTLS + OAuth2) in the same bank service."],
     ["Segmento P de um arquivo de remessa do Sicoob: um boleto por registro, cada campo numa posição fixa, exatamente 240 caracteres.",
      "Valores em centavos, sem vírgula; datas em DDMMAAAA.",
      "Inter e Itaú entram pelas APIs REST deles (mTLS + OAuth2), no mesmo serviço bancário."]),
    ("nfse", "lu-receipt-text", "NFS-e Nacional", "NFS-e Nacional", code(dps_xml(), "xml"),
     ["The DPS the SDK builds: the Id joins municipality, CNPJ, series and number into 45 characters.",
      "Signed with the company's A1 certificate (XMLDSig, RSA-SHA256, enveloped), sent gzipped and base64-encoded over mutual TLS.",
      "tpAmb 2 is the government's restricted production environment, used for testing."],
     ["A DPS que o SDK monta: o Id junta município, CNPJ, série e número em 45 caracteres.",
      "Assinada com o certificado A1 da empresa (XMLDSig, RSA-SHA256, enveloped), enviada compactada em gzip e base64 por TLS mútuo.",
      "tpAmb 2 é o ambiente de produção restrita do governo, usado para testes."]),
    ("meta", "si-whatsapp", "WhatsApp", "WhatsApp", code(ECHO, "json"),
     ["A coexistence echo: a message the business sent from the WhatsApp Business app on the phone.",
      "The module finds the account by WABA and phone number, checks Meta's signature, dedupes by wamid and posts it in the customer's conversation in Odoo.",
      "Without it, half of every conversation would be missing in Odoo."],
     ["Um eco de coexistência: uma mensagem que a empresa mandou pelo app WhatsApp Business no celular.",
      "O módulo acha a conta pelo WABA e pelo número, confere a assinatura da Meta, elimina duplicatas pelo wamid e publica na conversa do cliente no Odoo.",
      "Sem ele, metade de cada conversa faltaria no Odoo."]),
    ("zabbix", "lu-activity", "Zabbix → CMDB", "Zabbix → CMDB", code(ZABBIX, "json"),
     ["The host.get result the scheduled sync reads: host, status, interfaces, group and tags.",
      "Each host becomes a CMDB asset; status 0 means monitored, and only the category, product, doc and impact tags are kept.",
      "The asset then links to tickets, problems and changes in NexView ITSM."],
     ["O resultado do host.get que a sincronização agendada lê: host, status, interfaces, grupo e tags.",
      "Cada host vira um ativo do CMDB; status 0 significa monitorado, e só as tags category, product, doc e impact são mantidas.",
      "O ativo passa a se ligar a tickets, problemas e mudanças na NexView ITSM."]),
    ("mcp", "si-modelcontextprotocol", "MCP", "MCP", code(MCP, "json"),
     ["An AI assistant calling Odoo through the MCP connector: the first call is allowed, the second is refused.",
      "Access is granted per model and per operation; a model without a grant returns the same polite refusal, never the data.",
      "Tool errors come back as results with isError, so the assistant can explain them instead of crashing."],
     ["Um assistente de IA chamando o Odoo pelo conector MCP: a primeira chamada é permitida, a segunda é recusada.",
      "O acesso é concedido por modelo e por operação; um modelo sem permissão devolve sempre a mesma recusa educada, nunca o dado.",
      "Erros de ferramenta voltam como resultado com isError, para que o assistente explique em vez de quebrar."]),
]


ORDER = ["zabbix", "meta", "mcp", "nfse", "cnab"]  # most telling first; CNAB is the plainest


def main():
    PANELS.sort(key=lambda p: ORDER.index(p[0]))
    tabs, panels = [], []
    for i, (key, icon, en, pt, body, notes_en, notes_pt) in enumerate(PANELS):
        sel = "true" if i == 0 else "false"
        tabs.append(
            f'<button type="button" role="tab" id="wtab-{key}" aria-controls="wpanel-{key}" aria-selected="{sel}" data-wire="{key}">'
            f'<svg class="ic"><use href="#{icon}"/></svg><span class="en">{en}</span><span class="pt">{pt}</span></button>')
        notes = "".join(f'<li><span class="en">{html.escape(a)}</span><span class="pt">{html.escape(b)}</span></li>' for a, b in zip(notes_en, notes_pt))
        hidden = "" if i == 0 else " hidden"
        panels.append(
            f'<div class="wire-panel" role="tabpanel" id="wpanel-{key}" aria-labelledby="wtab-{key}"{hidden}>'
            f'<div class="wire-body">{body}</div><ul class="wire-notes">{notes}</ul></div>')
    section = (
        '<section id="wire">\n'
        '      <div class="rule" aria-hidden="true"></div>\n'
        '      <h2><span class="en">What goes over the wire</span><span class="pt">O que trafega nas integrações</span></h2>\n'
        '      <p class="sub en">Real message shapes from my integrations, with fictitious data. Pick a connection.</p>\n'
        '      <p class="sub pt">O formato real das mensagens das minhas integrações, com dados fictícios. Escolha uma conexão.</p>\n'
        '      <div class="wire-tabs" role="tablist" aria-label="Integrations">' + "".join(tabs) + '</div>\n'
        '      ' + "\n      ".join(panels) + '\n'
        '    </section>\n'
    )
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(section)
    print("wire.html", len(section), "bytes; cnab line ok")


if __name__ == "__main__":
    main()
