# 互联网求职知识图谱数据库设计 (Schema Design)

本图谱旨在为求职者提供智能化的岗位匹配与技能分析服务。通过构建“岗位-技能-公司”的核心三元组，帮助求职者快速定位目标岗位，并明确所需技能栈。

## 核心节点 (Nodes)

### 1. Job (岗位)
核心实体，代表具体的招聘职位。
*   **Properties**:
    *   `id`: String (唯一标识，UUID或URL哈希)
    *   `title`: String (岗位名称，如 "高级Python后端工程师")
    *   `description`: String (职位描述全文)
    *   `salary_min`: Integer (最低月薪，单位：元)
    *   `salary_max`: Integer (最高月薪，单位：元)
    *   `salary_unit`: String (薪资单位，默认 "Month")
    *   `experience_req`: String (经验要求，如 "3-5年")
    *   `education_req`: String (学历要求，如 "本科")
    *   `job_type`: String (全职/实习/兼职)
    *   `created_at`: DateTime (发布时间)
    *   `url`: String (原始招聘链接)

### 2. Company (公司)
招聘方实体。
*   **Properties**:
    *   `name`: String (公司全称，唯一)
    *   `industry`: String (所属行业，如 "互联网/电商")
    *   `size`: String (人员规模，如 "100-499人")
    *   `description`: String (公司简介)
    *   `website`: String (官网链接)

### 3. Skill (技能)
岗位要求的硬技能或软技能，是匹配的核心。
*   **Properties**:
    *   `name`: String (技能名称，唯一，如 "Python", "Docker", "沟通能力")
    *   `category`: String (分类，如 "Language", "Framework", "Tool", "Soft Skill")
    *   `description`: String (技能简介，供 RAG 检索使用)
    *   `alias`: List<String> (别名列表，如 ["JS", "ECMAScript"] 对应 "JavaScript")

### 4. Location (地点)
工作地点，支持层级查询（城市 -> 区域）。
*   **Properties**:
    *   `name`: String (地点名称，唯一，如 "北京", "海淀区")
    *   `level`: String (行政级别，如 "City", "District")

### 5. Benefit (福利)
公司提供的福利待遇。
*   **Properties**:
    *   `name`: String (福利名称，唯一，如 "15薪", "六险一金", "弹性工作")

### 6. Education (学历)
标准化的学历要求节点。
*   **Properties**:
    *   `level`: String (学历等级，唯一，如 "Bachelor", "Master", "PhD")

### 7. Category (岗位分类)
职位的职能分类。
*   **Properties**:
    *   `name`: String (分类名称，唯一，如 "后端开发", "人工智能", "产品经理")

### 8. KnowledgeArticle (知识文章) ⭐ 新增
RAG 知识库的核心节点，存储面试题、行业知识、技能学习路径等文章，供 LangChain 检索。
*   **Properties**:
    *   `id`: String (唯一标识，UUID)
    *   `title`: String (文章标题)
    *   `content`: String (正文内容，供 LLM 检索)
    *   `type`: String (文章类型：`"interview_qa"` | `"career_guide"` | `"skill_tutorial"`)
    *   `source`: String (来源，如 "LeetCode", "掘金", "官方文档")
    *   `created_at`: DateTime (收录时间)

---

## 关系定义 (Relationships)

### 1. 招聘关系
*   `(:Company)-[:OFFERS]->(:Job)`
    *   表示某公司发布了某岗位。

### 2. 技能需求 (核心)
*   `(:Job)-[:REQUIRES_SKILL {priority: '...', level: '...'}]->(:Skill)`
    *   **Properties**:
        *   `priority`: String ("must_have" | "nice_to_have") - 区分硬性要求和加分项。
        *   `level`: String ("entry", "intermediate", "expert") - 要求的熟练度。

### 3. 地理位置
*   `(:Job)-[:LOCATED_IN]->(:Location)`
    *   岗位的工作地点。
*   `(:Company)-[:LOCATED_IN]->(:Location)`
    *   公司的总部或分部地点。

### 4. 福利待遇
*   `(:Job)-[:PROVIDES_BENEFIT]->(:Benefit)`
    *   岗位承诺的福利。

### 5. 学历要求
*   `(:Job)-[:REQUIRES_DEGREE]->(:Education)`
    *   岗位的最低学历门槛。

### 6. 岗位归属
*   `(:Job)-[:BELONGS_TO]->(:Category)`
    *   岗位所属的职能类别。

### 7. 技能前置关系 ⭐ 新增
*   `(:Skill)-[:PREREQUISITE_OF]->(:Skill)`
    *   表示学习目标技能前需要先掌握前置技能。示例：`Python -[:PREREQUISITE_OF]-> Flask`

### 8. 技能共现关系 ⭐ 新增
*   `(:Skill)-[:CO_OCCURS_WITH {weight: Integer}]->(:Skill)`
    *   **Properties**:
        *   `weight`: Integer (共现次数，由爬取数据批量计算，越高说明两项技能越常一起出现在同一职位)
    *   表示两种技能在职位需求中高频共现，帮助求职者发现技能组合规律。

### 9. RAG 知识覆盖关系 ⭐ 新增
*   `(:KnowledgeArticle)-[:COVERS]->(:Skill)`
    *   文章所涉及的技能，用于 RAG 按技能检索相关知识。
*   `(:KnowledgeArticle)-[:COVERS]->(:Category)`
    *   文章所涉及的职能方向，用于 RAG 按岗位类别检索。

### 10. Location 行政层级 ⭐ 新增
*   `(:Location {level:'District'})-[:BELONGS_TO]->(:Location {level:'City'})`
    *   区/县属于城市，支持"北京海淀区"向上聚合到"北京"的层级查询。

---

## 索引与约束 (Constraints & Indexes)

为了保证数据质量和查询性能，我们实施以下约束：

*   **唯一性约束 (Unique Constraints)**:
    *   `Job(id)`
    *   `Company(name)`
    *   `Skill(name)`
    *   `Location(name)`
    *   `Benefit(name)`
    *   `Education(level)`
    *   `Category(name)`
    *   `KnowledgeArticle(id)` ⭐ 新增

*   **全文索引 (Fulltext Indexes)**:
    *   `job_search_index`: 对 `Job(title, description)` 建立索引，支持关键词搜索。
    *   `skill_search_index`: 对 `Skill(name)` 建立索引，支持技能模糊匹配。
    *   `article_search_index`: 对 `KnowledgeArticle(title, content)` 建立索引，支持 RAG 全文检索。 ⭐ 新增

*   **范围索引 (Range Indexes)**:
    *   `job_created_at_index`: 对 `Job(created_at)` 建立索引，支持技能趋势的时间维度聚合查询（如"过去6个月需求上升最快的技能"）。 ⭐ 新增
