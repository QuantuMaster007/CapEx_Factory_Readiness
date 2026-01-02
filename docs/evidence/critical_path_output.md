# Critical Path Output

Program: **Phoenix-ETD**

Tool: **T-PH-01**

| program     | tool_id   | task_id   | task_name                   | workstream   | gate    | planned_start   | planned_finish   | status      | risk_level   | depends_on                                                                            |   cp_rank |
|:------------|:----------|:----------|:----------------------------|:-------------|:--------|:----------------|:-----------------|:------------|:-------------|:--------------------------------------------------------------------------------------|----------:|
| Phoenix-ETD | T-PH-01   | FT-10000  | Layout approval             | Facilities   | Install | 2025-09-15      | 2025-09-23       | In Progress | Low          | nan                                                                                   |         1 |
| Phoenix-ETD | T-PH-01   | FT-10007  | Tool delivered to dock      | SupplyChain  | Install | 2025-10-06      | 2025-10-16       | Done        | Medium       | Layout approval                                                                       |         2 |
| Phoenix-ETD | T-PH-01   | FT-10008  | Rigging scheduled           | SupplyChain  | Install | 2025-10-09      | 2025-10-11       | In Progress | High         | Tool delivered to dock                                                                |         3 |
| Phoenix-ETD | T-PH-01   | FT-10009  | Install tool in bay         | Hardware     | Install | 2025-10-12      | 2025-10-19       | In Progress | Low          | Power drop install,Tool delivered to dock,Rigging scheduled,Exhaust hookup,CDA hookup |         4 |
| Phoenix-ETD | T-PH-01   | FT-10011  | PLC flash + config          | Controls     | PowerOn | 2025-10-18      | 2025-10-26       | In Progress | Low          | Install tool in bay,Network VLAN approved                                             |         5 |
| Phoenix-ETD | T-PH-01   | FT-10012  | IO checkout                 | Controls     | PowerOn | 2025-10-21      | 2025-10-25       | Done        | Low          | PLC flash + config                                                                    |         6 |
| Phoenix-ETD | T-PH-01   | FT-10013  | Safety interlock validation | Controls     | PowerOn | 2025-10-24      | 2025-10-31       | Done        | Medium       | IO checkout                                                                           |         7 |
| Phoenix-ETD | T-PH-01   | FT-10014  | Dry run cycle               | Controls     | Comm    | 2025-10-27      | 2025-11-04       | In Progress | Low          | Safety interlock validation                                                           |         8 |
| Phoenix-ETD | T-PH-01   | FT-10015  | Process baseline run        | Hardware     | Comm    | 2025-10-30      | 2025-11-04       | Blocked     | Low          | Dry run cycle                                                                         |         9 |
| Phoenix-ETD | T-PH-01   | FT-10016  | SAT dry-run                 | Hardware     | SAT     | 2025-11-02      | 2025-11-05       | In Progress | Low          | Process baseline run,EHS walkdown                                                     |        10 |
| Phoenix-ETD | T-PH-01   | FT-10017  | SAT acceptance              | Hardware     | SAT     | 2025-11-05      | 2025-11-08       | Done        | Medium       | SAT dry-run                                                                           |        11 |