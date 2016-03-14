var React = require('react');
// -----------------------------------------------------------------------------

var MainContainer = React.creatClass({
	render: function () {
		return (
			<div className=main-container>
				{this.props.children}
			</div>
		)
	}
});
// -----------------------------------------------------------------------------

module.exports = MainContainer;
