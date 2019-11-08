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

class EditPost extends React.Component {
  state = {
    post: {
      title: '',
      description: '',
      content: ''
    },
    isUpdated: false,
    error: null
  }

  handleUpdate = () => {
    const { post } = this.state
    const { id, title, description, content } = post
    const url = `${API_PATH}/${id}`

    fetch(url, {
      method: 'POST',
      body: JSON.stringify({
        title,
        description,
        content
      }),
      headers: new Headers([
        ['content-type', 'application/json']
      ])
    })
      .then(response => {
        if (response.ok) {
          this.setState({ isUpdated: true })
        } else {
          this.setState({ error: 'Unable to update post' })
        }
      })
      .catch(() => {
        this.setState({ error: 'Unable to update post' })
      })
  }

  componentDidMount () {
    const { match } = this.props
    const url = `${API_PATH}/${match.params.id}`
    fetch(url)
      .then(response => {
        if (response.ok) {
          response.json()
            .then(post => {
              this.setState({ post })
            })
            .catch(() => {
              this.setState({ error: 'Unable to read post' })
            })
        }
      })
      .catch(() => {
        this.setState({ error: 'Unable to read post' })
      })
  }

  handleChange = (post, key, value) => {
    this.setState({ post: { ...post, [key]: value } })
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
          onSubmit={this.handleUpdate}
          submitContent='Save'
        />
      </div>
    )
  }

  render () {
    if (this.state.isUpdated === true) {
      return this.renderRedirect()
    } else if (this.state.error) {
      return this.renderDialog()
    } else {
      return this.renderContent()
    }
  }
}

EditPost.apply.propTypes = {
  classes: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired
}

export default withStyles(styles)(EditPost)
