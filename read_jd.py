#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
read_jd.py — 从求职管家的私有 Gist 云端备份读取 JD 数据（供 AI 本地分析用）

工作流：
  1. 在桌面文件「读JD令牌.txt」里放一行：GITHUB_TOKEN=ghp_xxx（需 gist 权限）
     可选再放一行：GIST_ID=你的gist编号（不填则脚本自动按 jobtrack.json 发现）
     —— 可以同时放多把令牌，脚本会自动尝试每一把，哪把带 gist 权限就用哪把
  2. 运行：python3 read_jd.py
  3. 脚本输出所有「未删除」记录的 JD 结构化清单

说明：
  - 云端真实字段为中文：公司 / 职位 / 薪资 / JD原文 / 投递状态 / 录入时间 / 更新时间 / id / _deleted
  - 账号下可能存在多个 jobtrack.json Gist，脚本自动选取「记录数最多」的那个
  - _deleted == 'True' 的记录视为已删除，自动跳过

安全：令牌只从本地文件读，绝不打印、绝不进聊天/日志。
"""
import json
import os
import sys
import urllib.request
import urllib.error

TOKEN_FILE = os.path.expanduser("~/Desktop/读JD令牌.txt")
GIST_FILENAME = "jobtrack.json"
API = "https://api.github.com"


def collect_creds():
    tokens = []
    gist_id = ""
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                if "=" in s:
                    key, _, val = s.partition("=")
                    key = key.strip().upper()
                    val = val.strip().strip('"').strip("'")
                    if key == "GIST_ID":
                        gist_id = val
                        continue
                    if key == "GITHUB_TOKEN" and val:
                        if val not in tokens:
                            tokens.append(val)
                        continue
                if s.startswith("ghp_") or s.startswith("github_pat_"):
                    if s not in tokens:
                        tokens.append(s)
    except FileNotFoundError:
        pass
    return tokens, gist_id


def api_get(path, token):
    req = urllib.request.Request(API + path, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "User-Agent": "jobsteward-jd-reader",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def is_deleted(rec):
    return str(rec.get("_deleted", "")).strip().lower() == "true"


def active_records(payload):
    recs = payload.get("records", []) or []
    return [r for r in recs if not is_deleted(r)]


def discover(token, explicit_gist_id=None):
    """返回 (gist_id, status)。status ∈ {OK, NO_AUTH, EMPTY, NO_MATCH}"""
    if explicit_gist_id:
        return (explicit_gist_id, "OK")
    try:
        list_data = api_get("/gists?per_page=100", token)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return (None, "NO_AUTH")
        raise
    cands = [g for g in list_data if g.get("files") and GIST_FILENAME in g["files"]]
    if not cands:
        return (None, "NO_MATCH" if list_data else "EMPTY")
    # 选「未删除记录数最多」的那个 gist（避免选到空备份）
    best = None
    best_n = -1
    for g in cands:
        try:
            c = api_get("/gists/" + g["id"], token)["files"][GIST_FILENAME].get("content")
            p = json.loads(c) if c else {}
            n = len(active_records(p))
        except Exception:
            n = -1
        if n > best_n:
            best_n, best = n, g["id"]
    if best is None:
        return (None, "NO_MATCH")
    return (best, "OK")


def main():
    tokens, gist_id = collect_creds()
    if not tokens:
        print("❌ 未在桌面「读JD令牌.txt」找到任何 GITHUB_TOKEN（需 gist 权限的令牌）。")
        sys.exit(1)

    print("🔍 检测到 %d 个候选令牌，逐个尝试带 gist 权限的那把…" % len(tokens))
    used_token = None
    used_gist_id = None
    flags = []
    for idx, tk in enumerate(tokens, 1):
        try:
            gid, flag = discover(tk, gist_id if idx == 1 else None)
        except urllib.error.HTTPError as e:
            flag, gid = "NO_AUTH", None
        flags.append((idx, flag))
        if flag == "OK" and gid:
            used_token, used_gist_id = tk, gid
            break
        gist_id = gist_id if idx == 1 else ""

    if not used_token:
        print("❌ 所有候选令牌都读不到 Gist：")
        for idx, flag in flags:
            if flag == "NO_AUTH":
                print("   · 第 %d 把：令牌无效/无权限（401/403，可能已过期）" % idx)
            elif flag == "EMPTY":
                print("   · 第 %d 把：能认证但 /gists 为空 → 这把【没有 gist 权限】（多半只勾了 repo）" % idx)
            elif flag == "NO_MATCH":
                print("   · 第 %d 把：账号下没有 jobtrack.json 备份" % idx)
        print("\n💡 解决：去 GitHub 建一把【只勾 gist 权限】的 classic token（90 天过期），")
        print("   替换 GITHUB_TOKEN= 那行后重跑。")
        sys.exit(1)

    gist = api_get("/gists/" + used_gist_id, used_token)
    f = gist.get("files", {}).get(GIST_FILENAME)
    content = f.get("content") if f else None
    if not content:
        print("❌ gist 中未找到 jobtrack.json 内容。")
        sys.exit(1)
    payload = json.loads(content)
    records = active_records(payload)

    total = len(payload.get("records", []) or [])
    print("✅ 成功读取云端备份（用第 %d 把令牌）。Gist=%s" % (
        [i for i, fl in flags if fl == "OK"][0] if any(fl == "OK" for _, fl in flags) else 1, used_gist_id))
    print("   总记录 %d 条，其中已删除 %d 条，有效 %d 条\n" % (total, total - len(records), len(records)))
    print("=" * 70)

    for i, r in enumerate(records, 1):
        company = r.get("公司", "") or ""
        position = r.get("职位", "") or ""
        salary = r.get("薪资", "") or ""
        status = r.get("投递状态", "") or ""
        jd = r.get("JD原文", "") or ""
        created = r.get("录入时间", "") or ""
        updated = r.get("更新时间", "") or ""
        print("\n【%d】%s · %s" % (i, company or "(未填公司)", position or "(未填岗位)"))
        if status:
            print("   投递状态：%s" % status)
        if salary:
            print("   薪资：%s" % salary)
        if created or updated:
            print("   录入/更新：%s / %s" % (created, updated))
        if jd:
            print("   ── JD 原文 ──")
            for line in jd.splitlines():
                print("   " + line)
        else:
            print("   （本条无 JD 原文）")
    print("\n" + "=" * 70)
    print("提示：以上为云端 Gist 最新备份（已过滤已删除）。如需据此做简历定制，告诉我目标岗位编号即可。")


if __name__ == "__main__":
    main()
