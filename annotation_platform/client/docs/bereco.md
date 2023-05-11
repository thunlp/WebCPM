# bereco

## 事件说明

每个事件包含一些通用的数据，签名如下：

```typescript
// 内容类型
enum CONTENT_TYPE {
  // 搜索结果 0 
  SEARCH_RESULT,
  // 结果的详情页面 1
  RESULT_TARGET_PAGE,
}

{
	// 当前检索关键词
	keyword: string;
	// 触发时间 为时间戳
	triggerAt: number;
	// 内容栈深度
	stackLength: number;
	// 当前在第几步
	step: number;
	// 记录id
	traceId: string;
	// 当前页面信息
	currentPageInfo: {
	  // 页面标题
		title: string;
		// 页面链接
		href: string;
		// 类型
		type: CONTENT_TYPE;
		// 内容区域的滚动条位置
		scrollTop: number;
	};
  // 动作类型
  action: string;
  // 动作额外携带的数据
  details: { 
  	[propName: string]: any;
  };
}
```



### RECORD_START

开启记录，对应打开右上角的开关。

```tsx
action: 'RECORD_START'
details: {}
```

### RECORD_CLOSE

关闭记录，对应到关闭右上角的开关。

```tsx
action: 'RECORD_CLOSE'
details: {
  // 摘要
	digests: {
    // 摘录时间
		createdAt: number;
    // 摘要内容
		content: string;
	}[]
}
```

### PRESS_SEARCH

点击搜索按钮。

```tsx
action: 'PRESS_SEARCH'
details: {
  // 搜索的关键词
	keyword: string;
}
```

### LOAD_PAGE_DETAIL

进入到一个搜索结果页面。

```tsx
action: 'LOAD_PAGE_DETAIL'
details: {
	// 结果页面
	href: string;
}
```

### PAGE_GO_BACK

返回上一页。

```tsx
action: 'PAGE_GO_BACK'
details: {}
```

### TRIGGER_SCROLL_UP

点击向上翻页。

```tsx
action: 'scrollUp'
details: {}
```

### TRIGGER_SCROLL_DOWN

点击向下翻页。

```tsx
action: 'TRIGGER_SCROLL_DOWN'
details: {}
```

### ADD_DIGEST

添加选中的内容为摘要。

```tsx
action: 'ADD_DIGEST'
details: {
	// 摘要
	text: string;
}
```

### FIND

点击查找按钮。

```tsx
action: 'FIND'
details: {
	// 查找的内容
	findKeyword: string;
	// 当前查找的索引
	findIndex: number;
	// 查找结果的个数
	findResultLength: number;
}
```

### FIND_NEXT

点击查找下一个按钮。

```tsx
action: 'FIND'
details: {
	// 查找的内容
	findKeyword: string;
	// 当前查找的索引
	findIndex: number;
	// 查找结果的个数
	findResultLength: number;
}
```

