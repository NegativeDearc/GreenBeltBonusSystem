# CIS Score System #
---
有史以来做的最复杂的一个系统，是《基于FLASK的WEB开发》的读后作品。

前端基于Bootstrap，后台是Flask，数据库是Sqlite3，经过几次重构，现使用SQLAlchemy做连接层。

**TODO**

- 完成一次完整的测试
- 使用缓存提高性能
- 继续改进代码质量
- 关注JS/AJAX技术

**介绍**

---

#### 首页界面 ####

![首页](http://i.imgur.com/KJrqewH.png)

#### 搜索界面 ####
使用jQuery AutoComplete 插件完成搜索，颜色搭配，页面布局扒自Bootstrap选站。

![search](http://i.imgur.com/BPLn3Ai.png)

**TODO**

- 网站挂在Nignx后，闲杂导致外网IP地址无法获取，如何解决？

#### 管理员界面 ####
使用jQuery Accordion 对页面进行折叠，节约版面。使用jQuery QueryBuilder插件生成Core SQL完成搜索和筛选

![admin](http://i.imgur.com/mg3Iia3.png)

#### 报表系统 ####
使用Bootstrap-datetimepicker插件，使用bootstrap table expandable，以及Python Prettytable完成折叠设计。

![report](http://i.imgur.com/oAqsGaM.png)
