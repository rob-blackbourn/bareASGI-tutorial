import React from 'react'
import PropTypes from 'prop-types'
import { Redirect } from 'react-router-dom'
import { withStyles } from '@material-ui/core/styles'
import PostEditor from './PostEditor'
import SimpleDialog from './SimpleDialog'
import { API_PATH } from '../config'

const styles = theme => ({
  root: {
    margin: theme.spacing(2)
  }
})

class CreatePost extends React.Component {
  state = {
    post: {
      title: '',
      description: '',
      content: ''
    },
    isCreated: false,
    error: null
  }

  handleCreate = () => {
    const { post } = this.state

    fetch(API_PATH, {
      method: 'POST',
      body: JSON.stringify({ ...post }),
      headers: new Headers([
        ['content-type', 'application/json']
      ])
    })
      .then(response => {
        if (response.ok) {
          this.setState({ isCreated: true })
        } else {
          this.setState({ error: 'Unable to save post' })
        }
      })
      .catch(() => {
        this.setState({ error: 'Unable to save post' })
      })
  }

  handleChange = (post, key, value) => {
    this.setState({
      post: {
        ...post,
        [key]: value
      }
    })
  }

  handleDismissDialog = () => {
    this.setState({ error: null })
  }

  renderRedirect = () => {
    return <Redirect to='/index' />
  }

  renderDialog = () => {
    return (
      <SimpleDialog
        onClose={() => this.handleDismissDialog()}
        open={this.state.error !== null}
        dialogTitle='Error'
        dialogContent={this.state.error}
      />
    )
  }

  renderContent = () => {
    const { classes } = this.props
    const { post } = this.state

    return (
      <div className={classes.root}>
        <PostEditor
          title={post.title}
          onTitleChange={value => this.handleChange(post, 'title', value)}
          description={post.description}
          onDescriptionChange={value => this.handleChange(post, 'description', value)}
          content={post.content}
          onContentChange={value => this.handleChange(post, 'content', value)}
          onSubmit={this.handleCreate}
          submitContent='Create'
        />
      </div>
    )
  }

  render () {
    if (this.state.isCreated === true) {
      return this.renderRedirect()
    } else if (this.state.error) {
      return this.renderDialog()
    } else {
      return this.renderContent()
    }
  }
}

CreatePost.apply.propTypes = {
  classes: PropTypes.object.isRequired
}

export default withStyles(styles)(CreatePost)
