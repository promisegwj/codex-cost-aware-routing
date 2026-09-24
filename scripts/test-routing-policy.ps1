[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$routingRoot = Split-Path -Parent $PSScriptRoot
$toolRouting = Get-Content -LiteralPath 'E:\CodexWorkSpace\工作环境必要配置\tool-routing.json' -Raw | ConvertFrom-Json
$routingPython = $toolRouting.routes.'python.codexAutomation'.primary.path
if (-not (Test-Path -LiteralPath $routingPython)) { throw 'Configured bundled Python unavailable' }
$policyCheck = @'
import pathlib,sys,tomllib
r=pathlib.Path(sys.argv[1])
def read(p):
 with (r/p).open('rb') as f:return tomllib.load(f)
c=read('codex-home/routing-controls.toml')
m={'batch_worker':('gpt-5.6-luna','low','workspace-write'),'explorer':('gpt-5.6-luna','high','read-only'),'worker_standard':('gpt-5.6-luna','xhigh','workspace-write'),'worker_frontier':('gpt-6-astra','low','workspace-write'),'reviewer_risk':('gpt-6-astra','low','read-only'),'planner_frontier':('gpt-6-astra','medium','read-only'),'reviewer_final':('gpt-6-astra','medium','read-only'),'reasoning_specialist':('gpt-6-astra','medium','read-only')}
k=('model','model_reasoning_effort','sandbox_mode')
for role,v in m.items():
 assert tuple(c['model_roles'][role][x] for x in k)==v,role+' control'
 a=read('codex-home/agents/'+role+'.toml');assert tuple(a[x] for x in k)==v,role+' agent'
 print('PASS exact control/agent:',role)
for p,role in {'mini':'batch_worker','worker-high':'worker_standard','highrisk':'worker_frontier','planner':'planner_frontier','reasoning-specialist':'reasoning_specialist'}.items():
 a=read('codex-home/profiles/'+p+'.config.toml');assert tuple(a[x] for x in k[:2])==m[role][:2],p
for role,f in c['fallback_profiles'].items():
 a=read('codex-home/'+f['profile']);assert all(a[x]==f[x] for x in k),role
 assert c['model_roles'][role]['availability_gate']
 assert c['model_roles'][role]['fallback_profile']+'.config.toml'==pathlib.Path(f['profile']).name
root=read('codex-home/config-routing-snippet.toml');assert (root['model'],root['model_reasoning_effort'])==('gpt-5.6-sol','medium')
assert c['t2_policy']['frontier_escalation_effort']=='low'
assert 'frontier_escalation_triggers' in c['t2_policy'] and 'sol_high_escalation_triggers' not in c['t2_policy']
assert set(c['economics_policy']['routine_astra_roles'])=={'worker_frontier','reviewer_risk','planner_frontier','reviewer_final'}
assert all('reasoning_specialist' not in v for v in c['tier_defaults'].values())
e=c['exceptional_reasoning_policy'];assert e['role']=='reasoning_specialist' and e['require_gate_evidence']
assert c['model_roles']['reasoning_specialist']['automatic_tier_route'] is False
assert e['prompt_only_is_hard_isolation'] is False and e['route_blocked_if_enforced_read_only_required_but_unavailable']
assert 'medium reasoning inadequacy' in e['medium_to_high_rule'] and 'explicit user request' in e['xhigh_max_ultra_rule']
x=c['execution_mapping_policy'];assert x['compare_registered_model_effort_to_controls'] and x['require_exact_model_effort_availability']
assert x['prompt_only_is_hard_isolation'] is False and x['route_blocked_if_required_isolation_unavailable']
assert c['writer_policy']['single_active_writer_per_scope'] and c['routing']['hard_route_tiers']==['T3','T4']
snippet=(r/'codex-home/config-routing-snippet.toml').read_text(encoding='utf-8-sig')
assert 'available only through' not in snippet and 'Routine Astra low/medium' in snippet
reference=(r/'docs/references/model-economics-reference.2026-09-24.md').read_text(encoding='utf-8-sig')
assert 'Approved routing use' in reference and 'These routine Astra low/medium roles do not require' in reference
assert 'preserve the existing ordinary role matrix' not in reference and 'future Luna high/xhigh candidate' not in reference
assert 'failure_packet_demonstrates_assigned_route_failed_due_to_reasoning_limit_not_tool_environment_or_capacity' in e['allowed_gate_paths']
print('PASS profiles, fallbacks, root, ordinary/specialist separation, isolation and governance')
'@
$policyCheck | & $routingPython - $routingRoot
if ($LASTEXITCODE -ne 0) { throw 'Routing policy validation failed' }
Write-Host 'Routing policy validation passed.'
